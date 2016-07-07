import re
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
			self.print_help()
		elif len(args) != 1:
			self.show_environment()
		else:
			pair = args[0].split("=")
			if len(pair) == 2 and self.pattern.match(pair[0]):
				self.shell.environment[pair[0]] = pair[1]
			else:
				self.shell.message("export error", "Can't export variables to environment", False)
		return constants.SHELL_STATUS_RUN

	def show_environment(self):
		pass