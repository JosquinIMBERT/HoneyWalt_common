class Controller:
	def __init__(self):
		self.socket = None

	def __del__(self):
		del self.socket

	# Func result is a dictionary with the following keys:
	#	"success" (mandatory): boolean that indicates whether the function succeeded or not
	#	"answer" (optional): answer object in case of success
	#	"msg" (optional): error message in case of fail
	def exec(self, func, *args, **kwargs):
		res = func(*args, **kwargs)
		self.socket.send_obj(res)