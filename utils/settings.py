# External
import json

# Internal
from common.utils.files import *

def get(name):
	with open(to_root_path("etc/settings.cfg"), "r") as settings_file:
		settings = json.load(settings_file)

	return settings[name]