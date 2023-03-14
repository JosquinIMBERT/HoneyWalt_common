class Controller:
	def __init__(self):
		self.socket = None
		self.name = None

	def __del__(self):
		del self.socket

	# Get the class name to generate logs (this class is abstract)
	def name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	# Func result is a dictionary with the following keys:
	#	"success" (mandatory): boolean that indicates whether the function succeeded or not
	#	"answer" (optional): answer object in case of success
	#	INFO/ERROR/WARNING/FATAL (optional): message for the client
	def exec(self, func, *args, **kwargs):
		res = func(*args, **kwargs)
		self.socket.send_obj(res)