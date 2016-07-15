import re
import os
from jadsh.builtin import Builtin
import jadsh.constants as constants

class export(Builtin):
	"""
	Export variables to the local shell environment
	Usage: `export VARIABLE=value`
	"""

	def setup(self):
		self.pattern = re.compile("([A-Za-z])\w+")

	def execute(self, *args):
		if "--help" in args:
			self.help()
		elif len(args) == 0:
			self.show_environment()
		else:
			pair = args[0].split("=")
			if len(pair) == 2 and self.pattern.match(pair[0]):
				os.environ[str(pair[0])] = str(pair[1])
			else:
				self.shell.message("export error", "Can't export variables to environment", False)
		return constants.SHELL_STATUS_RUN

	def show_environment(self):
		for key in os.environ:
			self.shell.stdout.write(str(key) + " " + str(os.getenv(key)) + "\n")