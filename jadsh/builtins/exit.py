import sys
from jadsh.builtin import Builtin
import jadsh.constants as constants

class exit(Builtin):
	def execute(self):
		sys.stdout.write("\n" + "Bye!" + "\n")
		return constants.SHELL_STATUS_STOP
