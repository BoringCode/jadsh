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
			return constants.SHELL_STATUS_RUN
		else:
			self.shell.stdout.write("\n" + "Bye!" + "\n")
			return constants.SHELL_STATUS_STOP
