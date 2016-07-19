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
		self.pattern = re.compile("^([a-zA-Z1-9_])+$")

	def execute(self, *args):
		if "--help" in args:
			self.help()
		elif len(args) == 0:
			self.show_environment()
		else:
			for arg in args:
				pair = arg.split("=")
				if len(pair) <= 2 and self.pattern.match(pair[0]):
					os.environ[str(pair[0])] = self.cleanToken(pair[1]) if len(pair) == 2 else ""
				else:
					self.screen.message("export error", "Can't export variables to environment", False)
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}

	def cleanToken(self, token):
		"""
		Remove wrapping quotation marks and other elements from token
		"""
		if len(token) == 0: return token
		quotes = "'\""
		if len(token) > 1 and token[0] in quotes and token[-1] in quotes:
			token = token[1:-1]
		token = token.replace("\\", "")
		return str(token)

	def show_environment(self):
		for key in os.environ:
			self.screen.write("%s %s\n", (str(key), str(os.environ[key])), False)
		self.screen.flush()