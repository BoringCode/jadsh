import os
import sys
from jadsh.constants import *

class reload:
	def execute(self, parent):
		"""
		Super ugly way to detect how I should relaunch this thing
		"""
		path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/" + os.path.basename(sys.argv[0])
		if ".py" not in path:
			path += ".py"
		os.execvp("python", ["python", path])
		sys.stdout.flush()
		return SHELL_STATUS_RUN