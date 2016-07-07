import re
from jadsh.builtin import Builtin
import jadsh.constants as constants

class export(Builtin):
	def setup(self):
		self.pattern = re.compile("([A-Za-z])\w+")
		
	def execute(self, variable, *args):
		pair = variable.split("=")
		if len(pair) == 2 and len(args) == 0 and self.pattern.match(pair[0]):
			self.shell.environment[pair[0]] = pair[1]
		else:
			self.shell.message("export error", "Can't export variables to environment", False)
		return constants.SHELL_STATUS_RUN