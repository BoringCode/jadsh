class Builtin:
	def __init__(self, shell):
		# Keep reference back to the shell (useful for querying information, etc...)
		self.shell = shell
		self.setup()

	def setup(self):
		pass

	def execute(self, *args):
		pass

	def help(self):
		import inspect

		help_text = inspect.getdoc(self)
		if help_text is None:
			self.shell.message("Help error", "This program (" + self.__class__.__name__ + ") doesn't not have a help text")
		else:
			self.shell.stdout.write(help_text)
			self.shell.stdout.write("\n")