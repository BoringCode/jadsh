import sys
from jadsh.constants import *


class exit:

	def execute(self, parent):
		sys.stdout.write("\n" + "Bye!" + "\n")
		return SHELL_STATUS_STOP
