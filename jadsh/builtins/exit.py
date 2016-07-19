from jadsh.builtin import Builtin
import jadsh.constants as constants

class exit(Builtin):
	"""	
       exit -- exit the shell

   Synopsis
       exit [STATUS]

   Description
       exit causes jadsh to exit.
    """

	def execute(self, *args):
		if "--help" in args:
			self.help()
			return {
				"returncode": constants.SHELL_STATUS_RUN
			}
		else:
			self.screen.write("\n%s\n", "Bye!")
			return {
				"returncode": constants.SHELL_STATUS_STOP
			}