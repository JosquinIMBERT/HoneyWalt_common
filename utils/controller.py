class Controller:
	def __init__(self):
		self.socket = None
		self.name = None

	def __del__(self):
		del self.socket

	# Get the class name to generate logs (this class is abstract)
	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def reconnect(self):
		return False

	# Func result is a dictionary with the following keys:
	#	"success" (mandatory): boolean that indicates whether the function succeeded or not
	#	"answer" (optional): answer object in case of success
	#	INFO/ERROR/WARNING/FATAL (optional): message for the client
	def exec(self, func, *args, **kwargs):
		res = func(*args, **kwargs)
		if not self.socket.send_obj(res):
			if self.reconnect():
				if self.socket.send_obj(res):
					return True
		return False