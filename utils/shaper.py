# External
import threading
import socket
import select
import queue
import time

# Internal
from common.utils.logs import *

class Shaper:
	def __init__(self, name="Shaper", timeout=5):
		self.keep_running = False
		self.thread = None
		self.lock = None
		self.name = name

		# Socket
		self.sock = None
		self.timeout = timeout

		# Peer's UDP host and port
		self.udp_host = None
		self.udp_port = None

		# Local UDP host and port
		self.udp_listen_host = None
		self.udp_listen_port = None

		# Peer
		self.peer = None

		# Messages to forward
		self.sending_queue = queue.Queue()

		# Selection lists
		self.rsocks = set()
		self.wsocks = set()

		# Additional socket to unblock the select operation before the timeout
		self.wake_addr = ("127.0.0.1", 0) # Port will be chosen randomly
		self.wake_sock_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.wake_sock_listen.bind(self.wake_addr)
		self.wake_addr = ("127.0.0.1", self.wake_sock_listen.getsockname()[1]) # Getting port number
		self.wake_sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.wake_msg = b"1"

	def __del__(self):
		if self.sock is not None:
			self.sock.close()
		if self.wake_sock_listen is not None:
			self.wake_sock_listen.close()
		if self.wake_sock_client is not None:
			self.wake_sock_client.close()

	def start(self):
		self.thread = threading.Thread(target=self.run)
		self.lock = threading.Lock()
		self.thread.start()

	def stop(self):
		self.keep_running = False
		self.wake()
		self.thread.join()

	def wake(self):
		self.wake_sock_client.sendto(self.wake_msg, self.wake_addr)

	def set_peer(self, peer):
		self.peer = peer

	def forward(self, packet):
		# Preparing to send
		self.lock.acquire()
		self.sending_queue.put(packet)
		self.wsocks.add(self.sock)
		self.lock.release()

		# Forcing select to unblock before the timeout
		self.wake()

	def log(self, lev, *args, **kwargs):
		log(lev, "["+self.name+"]", *args, **kwargs)

	# Abstract
	def prepare(self):
		pass

	def run(self):
		self.keep_running = True

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.prepare()

		self.rsocks = set([self.sock, self.wake_sock_listen])
		self.wsocks = set()

		while self.keep_running:
			r, w, _ = select.select(list(self.rsocks), list(self.wsocks), [], self.timeout)

			if len(r)<=0 and len(w)<=0:
				self.log(DEBUG, "Data Timeout")
				continue

			# Browing Read Sockets
			for s in r:
				if s == self.wake_sock_listen:
					self.log(DEBUG, "Breaking select")
					self.wake_sock_listen.recvfrom(1024)
					continue
				else:
					self.handle_read(s)

			# Browsing Write Sockets
			for s in w:
				self.handle_write(s)

	def handle_read(self, s):
		data, (self.udp_host, self.udp_port) = s.recvfrom(1024)
		if data and len(data)>0:
			self.peer.forward(data)
		else:
			self.log(DEBUG, "Received empty packet")

	def handle_write(self, s):
		if self.udp_host is None or self.udp_port is None:
			self.log(DEBUG, "UDP peer is not registered")
		else:
			self.lock.acquire()
			data = self.sending_queue.get()
			self.lock.release()

			sent = s.sendto(data, (self.udp_host, self.udp_port))

			self.lock.acquire()
			if sent<=0:
				self.log(DEBUG, "Failed to send data, reinserting")
				self.sending_queue.queue.insert(0, data)
			elif sent<len(data):
				self.sending_queue.queue.insert(0, data[sent:])
			else:
				if self.sending_queue.empty():
					self.wsocks.remove(s)
			self.lock.release()