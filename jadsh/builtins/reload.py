import os
import sys
from jadsh.builtin import Builtin
import jadsh.constants as constants

class reload(Builtin):
	def execute(self):
		"""
		Super ugly way to detect how I should relaunch this thing
		"""
		path = constants.BASE_DIR + "/" + "jadsh.py"
		# Replace current application with new executable
		os.execvp("python" + constants.PYTHON_VERSION, ["python" + constants.PYTHON_VERSION, path])