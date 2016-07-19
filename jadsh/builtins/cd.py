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
		self.previous_directory = None

	def execute(self, path = os.getenv("HOME", "~"), *args):
		if "--help" in path or "--help" in args:
			self.help()
		else:
			# Go back to previous directory
			if (path == "-"):
				if self.previous_directory is None:
					self.message("cd", "Hit end of history...")
					return constants.SHELL_STATUS_RUN
				else:
					path = self.previous_directory
			# Sometimes the user removes the previous directory which  is dumb
			try:
				self.previous_directory = os.getcwd()
			except:
				self.previous_directory = path
			path = os.path.expanduser(path)
			try:
				os.chdir(path)
			except:
				self.screen.message("cd", "The directory \"%s\" does not exist" % path)
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}
