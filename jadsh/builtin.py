import sys

from jadsh.screen import Screen

class Builtin:
	def __init__(self, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
		# Set stdin and stdout
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr

		# Create screen object to output text to terminal
		self.screen = Screen(stdin = self.stdin, stdout = self.stdout, stderr = self.stderr)

		self.setup()

	def setup(self):
		pass

	def execute(self, *args):
		pass

	def help(self):
		import inspect

		help_text = inspect.getdoc(self)
		if help_text is None:
			self.screen.message("Help error", "This program (" + self.__class__.__name__ + ") doesn't not have a help text")
		else:
			self.screen.write("%s\n", help_text)