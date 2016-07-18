import os
from jadsh.runner import Runner
from jadsh.builtin import Builtin
import jadsh.constants as constants

class _and(Builtin):
	"""
	and -- conditionally execute a command

	Synopsis
		COMMAND1; and COMMAND2
	"""

	def setup(self):
		self.runner = Runner(self.stdin, self.stdout, self.stderr)

	def execute(self, *args):
		if "--help" in args or len(args) == 0:
			self.help()
		else:
			status = int(os.getenv("status", 0))
			if status == 0:
				results = self.runner.execute(args)
				if results["builtin"]:
					return {
						"returncode": results["status"]
					}
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}