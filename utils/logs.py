# External
import os, sys, traceback

global LOG_LEVEL, COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL
LOG_LEVEL = 1
DEBUG = 5
COMMAND = 4
INFO = 3
WARNING = 2
ERROR = 1
FATAL = 0

def get_trace(start_func="main", nb_off=2):
	calls = []
	start = False
	for frame in traceback.extract_stack():
		if frame.name == start_func:
			start = True
		elif start:
			calls += [ frame.name ]
	calls = ">".join(calls[:-nb_off])
	return calls

# Print a fatal error and exit
def eprint(*args, **kwargs):
    log(FATAL, *args, **kwargs)
    sys.exit(1)

def log(level, *args, **kwargs):
	if level <= LOG_LEVEL:
		if level == FATAL:
			#trace = get_trace(nb_off=3)+":"
			print("[FATAL]", *args, file=sys.stderr, flush=True, **kwargs)
		elif level == ERROR:
			#trace = get_trace(nb_off=3)+":"
			print("[ERROR]", *args, file=sys.stderr, flush=True, **kwargs)
		elif level == WARNING:
			#trace = get_trace()+":"
			print("[WARNING]", *args, flush=True, **kwargs)
		elif level == INFO:
			print("[INFO]", *args, flush=True, **kwargs)
		elif level == DEBUG:
			print("[DEBUG]", *args, flush=True, **kwargs)
		elif level == COMMAND:
			print("[COMMAND]", *args, flush=True, **kwargs)

def log_remote(level, log_level, out, err, *args, **kwargs):
	if level <= log_level:
		if level == FATAL:
			print("[FATAL]", *args, file=err, flush=True, **kwargs)
		elif level == ERROR:
			print("[ERROR]", *args, file=err, flush=True, **kwargs)
		elif level == WARNING:
			#trace = get_trace()+":"
			print("[WARNING]", *args, file=out, flush=True, **kwargs)
		elif level == INFO:
			print("[INFO]", *args, file=out, flush=True, **kwargs)
		elif level == DEBUG:
			print("[DEBUG]", *args, file=out, flush=True, **kwargs)
		elif level == COMMAND:
			print("[COMMAND]", *args, file=out, flush=True, **kwargs)

def set_log_level(log_level):
	global LOG_LEVEL

	if log_level=="FATAL":
		LOG_LEVEL = FATAL
	elif log_level=="ERROR":
		LOG_LEVEL = ERROR
	elif log_level=="WARNING":
		LOG_LEVEL = WARNING
	elif log_level=="INFO":
		LOG_LEVEL = INFO
	elif log_level=="DEBUG":
		LOG_LEVEL = DEBUG
	elif log_level=="CMD" or log_level=="COMMAND":
		LOG_LEVEL = COMMAND
	else:
		print("common.utils.logs.set_log_level: invalid log level")
		sys.exit(1)

def get_log_level():
	global LOG_LEVEL
	return LOG_LEVEL