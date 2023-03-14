# External
import os, pickle, socket, sys

# Internal
from common.utils.logs import *

# CONSTANTS
global OBJECT_SIZE, COMMAND_SIZE
OBJECT_SIZE = 4 # Objects size encoded on 4 bytes
COMMAND_SIZE = 1 # Commands encoded on 1 bytes

# There are two kinds of clients / servers:
#	- TCLIENT: Transport (Transport-level) Client
#	- HCLIENT: HoneyWalt (Application-level) Client
#	- TSERVER: Transport (Transport-level) Server
#	- HSERVER: HoneyWalt (Application-level) Server
#
# Any combination of two of these roles is possible. In Honeywalt we have:
#	Machine / socket 	| TCP		| HONEYWALT
#	--------------------+-----------+-----------
#	VM					| TCLIENT	| HSERVER
#	Door				| TSERVER	| HSERVER
#	Controller(-door)	| TCLIENT	| HCLIENT
#	Controller(-VM)		| TSERVER	| HCLIENT
#	Controller(-client)	| TSERVER	| HSERVER
#	Client 				| TCLIENT	| HCLIENT

class ProtoSocket:
	def __init__(self):
		self.socket = None
		self.name = None

	# Get the class name to generate logs (this class is abstract for Door and VM sockets)
	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def connected(self):
		return self.socket is not None

	def close(self):
		if self.socket is not None: self.socket.close()
		self.socket = None

	# Send an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def send_obj(self, obj):
		if not self.connected():
			log(ERROR, self.get_name()+".send_obj: Failed to send an object. The socket is not connected")
			return 0
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
			log(ERROR, self.get_name()+".send_cmd: Failed to send a command. The socket is not connected")
			return 0
		else:
			return self.send(cmd_to_bytes(cmd))

	# Receive a command (should be on COMMAND_SIZE bytes)
	def recv_cmd(self):
		if not self.connected():
			log(ERROR, self.get_name()+".recv_cmd: Failed to send a command. The socket is not connected")
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
			log(ERROR, self.get_name()+".get_answer: received an invalid answer")
			return None
		else: # VALID ANSWER
			# Logging warnings, errors, and fatal errors
			for level in [INFO, WARNING, ERROR, FATAL]:
				if level in res and isinstance(res[level], list):
					for msg in res[level]:
						log(level, msg)
					if level == FATAL:
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
		if not self.connected(): return None
		self.socket.settimeout(timeout)
		try:
			res = self.socket.recv(size)
		except socket.timeout:
			log(WARNING, self.get_name()+".recv: reached timeout")
			self.close()
			return None
		except KeyboardInterrupt:
			log(INFO, self.get_name()+".recv: received KeyboardInterrupt")
			self.close()
			return None
		except socket.error:
			log(WARNING, self.get_name()+".recv: received a connection error")
			self.close()
			return None
		except Exception as err:
			log(FATAL, self.get_name()+".recv: an unknown error occured")
			self.close()
			eprint(self.get_name()+".recv:", err)
		else:
			if not res:
				log(WARNING, self.get_name()+".recv: Connection terminated")
				self.close()
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
	def __init__(self, port, addr="", socktype=socket.AF_INET):
		self.socktype = socktype
		self.listen_socket = socket.socket(self.socktype, socket.SOCK_STREAM)
		self.socket = None
		self.remaddr = None # Remote Addr
		self.port = port
		self.addr = addr

	def __del__(self):
		if self.socket is not None:
			self.socket.close()
		if self.listen_socket is not None:
			self.listen_socket.close()

	def bind(self):
		try:
			self.listen_socket.bind((self.addr, self.port))
		except:
			log(DEBUG, self.get_name()+".bind: failed to bind socket")
			return False
		self.listen_socket.listen(1)
		return True

	# Accept a new client connection
	# Return:
	#	- None	-> Interrupted (the server should stop)
	#	- False	-> Reached timeout or got an other Exception (the server should keep running)
	#	- True	-> A new connection was accepted
	def accept(self, timeout=5.0):
		try:
			self.listen_socket.settimeout(timeout)
			self.socket, self.remaddr = self.listen_socket.accept()
		except KeyboardInterrupt:
			log(DEBUG, self.get_name()+".accept: received KeyboardInterrupt")
			return None
		except socket.timeout:
			return False
		except Exception as err:
			log(ERROR, self.get_name()+".accept: an error occured when waiting for a connection")
			log(ERROR, self.get_name()+".accept:", err)
			return False
		else:
			log(INFO, self.get_name()+".accept: accepted a new client")
			return True


class ClientSocket(ProtoSocket):
	def __init__(self, socktype=socket.AF_INET):
		self.socktype = socktype
		self.socket = None
		self.ip = None
		self.port = None

	def __del__(self):
		if self.socket is not None:
			self.socket.close()

	# ip and port are optional but need to be given at least for the first connection
	def connect(self, ip=None, port=None):
		self.ip = self.ip if ip is None else ip
		self.port = self.port if port is None else port
		self.socket = socket.socket(self.socktype, socket.SOCK_STREAM)
		try:
			self.socket.connect((self.ip, self.port))
		except:
			log(DEBUG, self.get_name()+".connect: failed to connect")
			return False
		else:
			return True

	# Run a complete "command (+subcommands) - data - answer" exchange on a TCLIENT+HCLIENT socket
	def exchange(self, commands=[], data=None, timeout=30, retry=1):
		res = None
		trials = 0
		reconnect = False
		while trials <= retry:
			trials += 1
			if reconnect:
				self.close()
				if not self.connect(): return None
				reconnect = False
			for cmd in commands:
				if self.send_cmd(cmd) == 0:
					reconnect = True
					break
			else:
				if data is not None and self.send_obj(data) <= 0:
					reconnect = True
					continue
				res = self.get_answer(timeout=timeout)
				if res is None: reconnect = True
				else: break
		return res

	# Overrides the ProtoSocket send_cmd method
	# Tries to reconnect to the server if we fail to send the command
	# By default, we only try to reconnect once.
	# Set retry to 0 if you do not want to retry, n if you want to retry n times
	# Outdated because send returns when data is put in buffer, not when it is acknowledged 
	# def send_cmd(self, cmd, retry=1):
	# 	cpt = 0
	# 	while cpt<=retry:
	# 		ret = ProtoSocket.send_cmd(self, cmd)
	# 		if ret > 0:
	# 			return ret
	# 		elif cpt<retry:
	# 			log(INFO, "trying to reconnect to the server")
	# 			self.connect()
	# 		cpt += 1
	# 	return 0