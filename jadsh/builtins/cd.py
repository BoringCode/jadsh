import os
from jadsh.builtin import Builtin
import jadsh.constants as constants

class cd(Builtin):
	"""	
	cd -- change directory

	Synopsis
	   cd [DIRECTORY]

	Description
	   cd changes the current working directory.

	   If DIRECTORY is supplied, it will become the new directory. If no parameter is given, the contents of the HOME
	   environment variable will be used.

	Examples
	   cd
	     changes the working directory to your home directory.

	   cd /usr/local/bin/
	     changes the working directory to /usr/local/bin         
	"""

	def setup(self):
		self.directory_history = []

	def execute(self, path = os.getenv("HOME", "~"), *args):
		if "--help" in path or "--help" in args:
			self.help()
		else:
			# Go back to previous directory
			if (path == "-"):
				path = self.directory_history[-1]
			self.directory_history.append(os.getcwd())
			path = os.path.expanduser(path)
			os.chdir(path)
		return constants.SHELL_STATUS_RUN
