# External
import os, pickle, socket, sys

# Internal
from utils.logs import *

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
			self.socket.send(serialize(obj))

	# Receive an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def recv_obj(self, timeout=30):
		bytlen = self.recv(size=OBJECT_SIZE, timeout=timeout)
		if bytlen is not None:
			bytobj = self.recv(size=int.from_bytes(bytlen, 'big'), timeout=timeout)
			if bytobj is not None:
				return deserialize(bytobj)
		return None

	# Send a command (should be on COMMAND_SIZE bytes)
	def send_cmd(self, cmd):
		if not self.connected():
			log(ERROR, self.name()+".send_cmd: Failed to send a command. The socket is not connected")
			return 0
		else:
			return self.socket.send(cmd_to_bytes(cmd))

	# Receive a command (should be on COMMAND_SIZE bytes)
	def recv_cmd(self):
		if not self.connected():
			log(ERROR, self.name()+".recv_cmd: Failed to send a command. The socket is not connected")
			return None
		else:
			bytes_cmd = self.recv(size=COMMAND_SIZE)
			if bytes_cmd:
				return bytes_to_cmd(bytes_cmd)
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
		if not res or not isinstance(res, dict) or not "success" in res: 
			log(ERROR, self.name()+".get_answer: received an invalid answer")
			return False
		else:
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
		return self.socket.send(bytes_msg)

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
			import glob
			if "SERVER" in dir(glob):
				glob.SERVER.stop()
		except Exception as err:
			print(err)
			eprint(self.name()+".recv: an unknown error occured")
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

def bytes_to_cmd(byt):
	return int.from_bytes(byt, 'big')

def to_nb_bytes(integer, nb):
	try:
		byt = integer.to_bytes(nb, 'big')
	except OverflowError:
		log(ERROR, "utils.sockets.to_nb_bytes: the object is too big")
		return bytes(0)
	return byt