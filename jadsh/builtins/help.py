import webbrowser
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
	def execute(self, path = "~", *args):
		if "--help" in path or "--help" in args:
			self.help()
		else:
			self.message("jadsh help", "Opening " + str(constants.HELP_URL) + "...", True)
			webbrowser.open(constants.HELP_URL)
		return {
			"returncode": constants.SHELL_STATUS_RUN
		}
