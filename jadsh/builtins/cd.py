import os
from jadsh.builtin import Builtin
import jadsh.constants as constants

class cd(Builtin):
	def setup(self):
		self.directory_history = []

	def execute(self, path):
		# Go back to previous directory
		if (path == "-"):
			path = self.directory_history[-1]
		self.directory_history.append(os.getcwd())
		path = os.path.expanduser(path)
		os.chdir(path)
		return constants.SHELL_STATUS_RUN
