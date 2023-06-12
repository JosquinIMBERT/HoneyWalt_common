# External
import json, rpyc

# Internal
from common.utils.logs import *
from common.utils.misc import *

class IPService(rpyc.Service):
	def __init__(self):
		self.ip = get_public_ip()

	def exposed_get_ip(self):
		return self.ip

class AbstractService(rpyc.Service):
	def __init__(self):
		self.remote_stdout = None
		self.remote_stderr = None
		self.loglevel = INFO
		self.conn = None
		self.remote_ip = None

	def __del__(self):
		del self.remote_stdout
		del self.remote_stderr
		del self.loglevel
		del self.conn
		del self.remote_ip

	def on_connect(self, conn):
		self.conn = conn
		self.remote_ip = conn.root.get_ip()
		log(INFO, self.__class__.__name__+": New connection from", self.remote_ip)

	def on_disconnect(self, conn):
		log(INFO, self.__class__.__name__+": End of connection with", self.remote_ip)

	def exposed_set_stdout(self, stdout):
		# TODO: verify what the client is giving as argument
		self.remote_stdout = stdout

	def exposed_set_stderr(self, stderr):
		# TODO: verify what the client is giving as argument
		self.remote_stderr = stderr

	def exposed_set_log_level(self, loglevel):
		if loglevel not in [COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL]:
			self.log(ERROR, "invalid loglevel")
		else:
			self.loglevel = loglevel

	def log(self, level, *args, **kwargs):
		if self.remote_stdout is not None and self.remote_stderr is not None:
			log_remote(level, self.loglevel, self.remote_stdout, self.remote_stderr, *args, **kwargs)

	def call(self, func, *args, **kwargs):
		return json.dumps(func(self, *args, **kwargs))

class FakeClient():
	def __init__(self, ignore_logs=False):
		self.remote_ip = "127.0.0.1"
		self.ignore_logs = ignore_logs

	def __del__(self):
		del self.remote_ip

	def log(self, level, *args, **kwargs):
		if not self.ignore_logs: log(level, *args, **kwargs)