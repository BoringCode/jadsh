import os
import sys
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
    It will completely wipe out your environment and will start the shell fresh.
    
	"""
	def execute(self, *args):
		if "--help" in args:
			self.help()
			return constants.SHELL_STATUS_RUN
		else:
			path = constants.BASE_DIR + "/" + "jadsh.py"
			# Replace current application with new executable
			os.execvp("python" + constants.PYTHON_VERSION, ["python" + constants.PYTHON_VERSION, path])