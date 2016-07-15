import os
from jadsh.builtin import Builtin
import jadsh.constants as constants

class reload(Builtin):
	"""
	reload -- dynamically restart jadsh

   Synopsis
    reload

   Description
    reload dynamically reloads jadsh.

    This is mainly a helper function with developing jadsh.     
	"""
	def execute(self, *args):
		if "--help" in args:
			self.help()
			return constants.SHELL_STATUS_RUN
		else:
			# Replace current application with new executable
			os.execvp("jadsh", ["jadsh"])