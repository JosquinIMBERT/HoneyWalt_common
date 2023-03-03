class Controller:
	def __init__(self):
		self.socket = None

	def __del__(self):
		del self.socket

	# Get the class name to generate logs (this class is abstract)
	def name(self):
		return self.__class__.__name__

	# Func result is a dictionary with the following keys:
	#	"success" (mandatory): boolean that indicates whether the function succeeded or not
	#	"answer" (optional): answer object in case of success
	#	"msg" (optional): error message in case of fail
	def exec(self, func, *args, **kwargs):
		res = func(*args, **kwargs)
		self.socket.send_obj(res)