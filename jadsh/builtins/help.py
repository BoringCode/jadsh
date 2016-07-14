import os
from jadsh.builtin import Builtin
import jadsh.constants as constants

class help(Builtin):
	"""	
	help -- display help about jadsh

   Synopsis
       help

   Description
       help gives you help

       See also: recursion

   Examples
       help
         Displays general help about jadsh
         
	"""

	def setup(self):
		pass

	def execute(self, path = "~", *args):
		if "--help" in path or "--help" in args:
			self.help()
		else:
			self.shell.message("jadsh help", "This will eventually display help", True)
		return constants.SHELL_STATUS_RUN
