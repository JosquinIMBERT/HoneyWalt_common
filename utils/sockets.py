# External
import os, pickle, socket, sys

# Internal
from common.utils.logs import *

# CONSTANTS
global OBJECT_SIZE, COMMAND_SIZE
OBJECT_SIZE = 4 # Objects size encoded on 4 bytes
COMMAND_SIZE = 1 # Commands encoded on 1 bytes

class ProtoSocket:
	def __init__(self):
		self.socket = None

	# Get the class name to generate logs (this class is abstract for Door and VM sockets)
	def name(self):
		return self.__class__.__name__

	def connected(self):
		return self.socket is not None

	# Send an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def send_obj(self, obj):
		if not self.connected():
			log(ERROR, self.name()+".send_obj: Failed to send an object. The socket is not connected")
		else:
			return self.send(serialize(obj))

	# Receive an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def recv_obj(self, timeout=30):
		bytlen = self.recv(size=OBJECT_SIZE, timeout=timeout)
		if bytlen is not None:
			bytobj = self.recv(size=bytes_to_int(bytlen), timeout=timeout)
			if bytobj is not None:
				return deserialize(bytobj)
		return None

	# Send a command (should be on COMMAND_SIZE bytes)
	def send_cmd(self, cmd):
		if not self.connected():
			log(ERROR, self.name()+".send_cmd: Failed to send a command. The socket is not connected")
			return 0
		else:
			return self.send(cmd_to_bytes(cmd))

	# Receive a command (should be on COMMAND_SIZE bytes)
	def recv_cmd(self):
		if not self.connected():
			log(ERROR, self.name()+".recv_cmd: Failed to send a command. The socket is not connected")
			return None
		else:
			bytes_cmd = self.recv(size=COMMAND_SIZE)
			if bytes_cmd:
				return bytes_to_int(bytes_cmd)
			else:
				return None

	# get_answer
	# Print the warnings, errors and fatal errors, get the answer
	# Return:
	#	- True if it is a success but their is no answer data
	#	- Answer (any kind of object) if it is a success and their is an answer data
	#	- False if it did not succeed
	def get_answer(self, timeout=30):
		res = self.recv_obj(timeout=30)
		if not res: # CONNECTION TERMINATED OR KEYBOARD INTERRUPTION
			return None
		elif not isinstance(res, dict) or not "success" in res: # INVALID ANSWER 
			log(ERROR, self.name()+".get_answer: received an invalid answer")
			return None
		else: # VALID ANSWER
			# Logging warnings, errors, and fatal errors
			if "warning" in res and isinstance(res["warning"], list):
				for warn in res["warning"]:
					log(WARNING, warn)
			if "error" in res and isinstance(res["error"], list):
				for error in res["error"]:
					log(ERROR, error)
			if "fatal" in res and isinstance(res["fatal"], list):
				for fatal in res["fatal"]:
					log(FATAL, fatal)
				sys.exit(1)

			# Checking success
			if res["success"]:
				if "answer" in res:
					return res["answer"]
				else:
					return True
			else:
				return False

	# Send data to the socket
	def send(self, bytes_msg):
		try:
			nb = self.socket.send(bytes_msg)
		except:
			return 0
		else:
			return nb

	# Receive data on socket, with a timeout
	def recv(self, size=2048, timeout=30):
		self.socket.settimeout(timeout)
		try:
			res = self.socket.recv(size)
		except socket.timeout:
			log(WARNING, self.name()+".recv: reached timeout")
			return None
		except KeyboardInterrupt:
			log(INFO, self.name()+".recv: received KeyboardInterrupt")
			return None
		except socket.error:
			log(WARNING, self.name()+".recv: received a connection error")
			return None
		except Exception as err:
			log(FATAL, self.name()+".recv: an unknown error occured")
			eprint(self.name()+".recv:", err)
		else:
			if not res:
				log(WARNING, self.name()+".recv: Connection terminated")
				return None
			return res


def serialize(obj):
	serial = pickle.dumps(obj)
	length = len(serial)
	bytlen = to_nb_bytes(length, OBJECT_SIZE)
	return bytlen+serial

def deserialize(strg):
	return pickle.loads(strg)

def cmd_to_bytes(cmd):
	return cmd.to_bytes(COMMAND_SIZE, 'big')

def bytes_to_int(byt):
	return int.from_bytes(byt, 'big')

def to_nb_bytes(integer, nb):
	try:
		byt = integer.to_bytes(nb, 'big')
	except OverflowError:
		log(ERROR, "common.utils.sockets.to_nb_bytes: the object is too big")
		return bytes(0)
	return byt


class ServerSocket(ProtoSocket):
	def __init__(self, port):
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = None
		self.addr = None
		self.port = port

	def __del__(self):
		if self.socket is not None:
			self.socket.close()
		if self.listen_socket is not None:
			self.listen_socket.close()

	def bind(self):
		try:
			self.listen_socket.bind(("", self.port))
		except:
			log(ERROR, self.name()+".connect: failed to bind socket")
			return False
		self.listen_socket.listen(1)
		return True

	# Accept a new client connection
	# Return:
	#	- None	-> Interrupted (the server should stop)
	#	- False	-> Reached timeout or got an other Exception (the server should keep running)
	#	- True	-> A new connection was accepted
	def accept(self, timeout=5):
		try:
			self.listen_socket.settimeout(timeout)
			self.socket, self.addr = self.listen_socket.accept()
		except KeyboardInterrupt:
			log(DEBUG, self.name()+".accept: received KeyboardInterrupt")
			return None
		except socket.timeout:
			return False
		except Exception as err:
			log(ERROR, self.name()+".accept: an error occured when waiting for a connection")
			log(ERROR, self.name()+".accept:", err)
			return False
		else:
			log(INFO, self.name()+".accept: accepted a new client")
			return True


class ClientSocket(ProtoSocket):
	def __init__(self, socktype=socket.AF_INET):
		self.socket = socket.socket(socktype, socket.SOCK_STREAM)

	def __del__(self):
		if self.socket is not None:
			self.socket.close()

	def connect(self, ip, port):
		try:
			self.socket.connect((ip, port))
		except:
			log(ERROR, self.name()+".connect: failed to connect")
			return False
		else:
			return True