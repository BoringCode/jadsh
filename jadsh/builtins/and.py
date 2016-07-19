import os
from jadsh.runner import Runner
from jadsh.builtin import Builtin
import jadsh.constants as constants

class _and(Builtin):
	"""
	and -- conditionally execute a command

	Synopsis
		COMMAND1; and COMMAND2

	Description
		and executes a command if the current exit status (set by the previous command) is equal to 0

		and does not change the current exit status
	"""

	def setup(self):
		self.runner = Runner(self.stdin, self.stdout, self.stderr)

	def execute(self, *args):
		if "--help" in args or len(args) == 0:
			self.help()
		else:
			status = int(os.getenv("status", constants.EXIT_CODE_SUCCESS))
			if status == constants.EXIT_CODE_SUCCESS:
				results = self.runner(args)
				if results["builtin"]:
					return {
						"returncode": results["status"]
					}
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}