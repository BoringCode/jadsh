import os
from jadsh.constants import *

class cd:

	def __init__(self):
		self.directory_history = []

	def execute(self, parent, path):
		# Go back to previous directory
		if (path == "-"):
			path = self.directory_history[-1]
		self.directory_history.append(os.getcwd())
		path = os.path.expanduser(path)
		os.chdir(path)
		return SHELL_STATUS_RUN
