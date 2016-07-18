import sys

class Builtin:
	def __init__(self, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
		# Set stdin and stdout
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
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
			self.stdout.write(help_text)
			self.stdout.write("\n")
			self.stdout.flush()

	def message(self, title, message, status = False):
		"""
		Display message in the terminal
		"""
		self.stdout.write(self.hilite("%s: " % str(title), status))
		self.stdout.write("%s\n" % str(message))
		self.stdout.flush()

	def hilite(self, string, status = False, bold = False):
		"""
		Generate bold, or colored string using ANSI escape codes

		@return String
		"""
		if not self.stdout.isatty(): return string
		attr = []
		if status:
			# green
			attr.append('32')
		else:
			# red
			attr.append('31')
		if bold:
			attr.append('1')
		return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)