# External
import json, os, requests, sys

# Internal
from utils.files import *

# Find an object in the "objects" list with field "field" equal "target"
def find(objects, target, field):
	for obj in objects:
		if obj[field] == target:
			return obj
	return None

# Find the id of an object in the "objects" list with field "field" equal "target"
def find_id(objects, target, field):
	i=0
	for obj in objects:
		if obj[field] == target:
			return i
		i += 1
	return -1

# Print the markdown help page from the documentation directory
def markdown_help(name):
	with open(to_root_path("doc/"+name+".md")) as file:
		try:
			from rich.console import Console, ConsoleOptions
			from rich.markdown import Markdown
			console = Console()
			#console.options.update(max_width=10000)
			console.print(Markdown(file.read(),
				inline_code_theme='ansi_white'
			))
		except ModuleNotFoundError:
			print("Consider installing rich for enhanced help pages")
			print("```pip3 install rich```")
			print(file.read())

def print_object_array(objects, fields):
	max_length = {}
	for field in fields:
		max_length[field] = len(field)

	for obj in objects:
		for field in fields:
			txt = obj.get(field) or ""
			if type(txt) is list:
				length = 0
				for elem in txt:
					length += len(str(elem))+1
				length-=1
			else:
				length = len(txt)
			if length > max_length[field]:
				max_length[field] = length

	break_size = 3
	line = ""
	separator = ""
	for field in fields:
		line += field + " " * (max_length[field] - len(field) + break_size)
		separator += "-" * max_length[field] + " " * break_size
	print(line)
	print(separator)
	for obj in objects:
		line = ""
		for field in fields:
			txt = obj.get(field) or ""
			if type(txt) is list:
				length = 0
				for i, elem in enumerate(txt):
					if i>0:
						line += ","
					line += str(elem)
					length += len(str(elem))+1
				length -= 1
			else:
				line += txt
				length = len(txt)
			line += " " * (max_length[field] - len(txt) + break_size)
		print(line)

# Extract the shortname from a cloneable image link
def extract_short_name(name):
	return (name.split("/", 1)[1]).split(":", 1)[0]

# Source: https://pytutorial.com/python-get-public-ip
def get_public_ip():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify = True)
    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
        exit()
    data = response.json()
    return data['ip']