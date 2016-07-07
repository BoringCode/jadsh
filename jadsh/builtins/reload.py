import os
import sys
from jadsh.constants import *

class reload:

	def execute(self, parent):
		path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/" + os.path.basename(sys.argv[0])
		os.execvp("python", ["python", path])
		sys.stdout.flush()
		return SHELL_STATUS_RUN