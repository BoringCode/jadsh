class Builtin:
	def __init__(self, shell):
		# Keep reference back to the shell (useful for querying information, etc...)
		self.shell = shell

		self.setup()

	def setup(self):
		pass

	def execute(self, *args):
		pass