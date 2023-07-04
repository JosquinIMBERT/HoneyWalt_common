# External
import os
from os.path import abspath, dirname, exists, join, isfile

# Get the path to the root of the application
def get_root_path():
	path = abspath(dirname(__file__))
	root = ["/"]+path.split("/")[:-3]
	return join(*root)

# get the path to a file in the application
def to_root_path(path):
	root_path = get_root_path()
	return join(root_path, path)

# delete files with a given suffix in a directory
def delete(directory, suffix=""):
	for name in os.listdir(directory):
		file = os.path.join(directory,name)
		if file.endswith(suffix):
			os.remove(file)

# delete a file from its name
def delete_file(file):
	if isfile(file):
		os.remove(file)