import os
from jadsh.runner import Runner
from jadsh.builtin import Builtin
import jadsh.constants as constants

class _or(Builtin):
	"""
	or -- conditionally execute a command

	Synopsis
		COMMAND1; or COMMAND2

	Description
		or executes a command if the current exit status (set by the previous command) is not equal to 0

		or does not change the current exit status
	"""

	def setup(self):
		self.runner = Runner(self.stdin, self.stdout, self.stderr)

	def execute(self, *args):
		if "--help" in args or len(args) == 0:
			self.help()
		else:
			status = int(os.getenv("status", constants.EXIT_CODE_SUCCESS))
			if status != constants.EXIT_CODE_SUCCESS:
				results = self.runner.execute(args)
				if results["builtin"]:
					return {
						"returncode": results["status"]
					}
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}