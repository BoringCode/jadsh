import os, sys

from jadsh.prompt import Prompt
import jadsh.constants as constants

class Screen:
	def __init__(self, prompt = Prompt(), stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
		self.prompt = prompt
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr

		self.screen = ""

		self.cursor = 0

	def __call__(self, *argv):
		self.draw(*argv)

	def updateCursor(self, position):
		self.cursor = self.cursor + int(position)

	def getCursor(self, text):
		if self.cursor < 0:
			self.cursor = 0
		elif self.cursor > len(text):
			self.cursor = len(text)
		return self.cursor

	def saveCursor(self):
		if self.stdout.isatty():
			self.write("\x1b7")

	def resetCursor(self):
		if self.stdout.isatty():
			self.write("\x1b8")

	def draw(self, *argv):
		"""
		Draw the terminal so the user can see it
		"""
		if self.stdout.isatty():
			# Reset cursor to previous position
			# TODO: Handle edge case when current line is at the bottom of the terminal
			self.screenAppend("\x1b8")

			# Hide the cursor
			self.screenAppend("\x1b[?25l");

			# Clear everything after the current line
			self.screenAppend("\x1b[J\r")

			# Save the current cursor position
			self.screenAppend("\x1b7")

		# Output all args to the terminal
		for arg in argv:
			self.screenAppend(arg)

		if self.stdout.isatty():
			self.screenAppend("\x1b[?25h") # Show cursor

			# Calculate cursor position and place at correct spot
			# TODO: Handle edge case when user input goes to more than 1 line
			position = len(argv[-1]) - self.getCursor(argv[-1])
			if position > 0:
				# Move cursor backwards
				self.screenAppend("\x1b[%sD" % str(position))

		if not self.stdout.isatty():
			self.screenAppend("\n")

		# Output everything to the screen
		self.write(self.screen)
		self.screen = ""

	def screenAppend(self, text):
		"""
		Add new text to the screen
		"""
		self.screen += str(text)

	def message(self, title, message, status = False):
		"""
		Display message in the terminal
		"""
		self.write(self.hilite("%s: " % str(title), status), flush = False)
		self.write("%s\n" % str(message))
		self.saveCursor()

	def write(self, prepared_string = "", items = None, flush = True):
		"""
		Output prepared string to terminal
		"""
		if items:
			self.stdout.write(str(prepared_string) % items)
		else:
			self.stdout.write(str(prepared_string))
		if flush: self.flush()

	def flush(self):
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