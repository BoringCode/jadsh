import string
from io import StringIO

from jadsh.shell import Shell
import jadsh.constants as constants

class Parser:
	"""A tokenizer that integrates with jadsh"""
	def __init__(self, shell):
		self.eof = None

		self.comments = "#"

		self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
		                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
		                  'ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
		                  'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')

		self.whitespace = ' \t\r\n'
		self.quotes = '\'"'
		self.escape = '\\'
		self.escapedquotes = '"'

	def parse(self, instream = None):
		if isinstance(instream, str):
			instream = StringIO(instream)
		self.instream = instream

		self.token = ''
		self.token_stack = []
		self.tokens = []

		tokens = self.read_tokens()

		return tokens

	def read_tokens(self):
		commands = []
		tokens = []
		token_stack = [] 
		token = ''

		while True:
			nextchar = self.instream.read(1)

			# EOF
			if nextchar is self.eof:
				break

			# Ignore comments
			if nextchar in self.comments:
				break

			# Split tokens on whitespace
			if nextchar in self.whitespace and len(token_stack) == 0:
				tokens.append(token)
				token = ''
				continue

			# Quotes
			if nextchar in self.quotes:
				state = None
				# Check if stack has characters on it
				if len(token_stack) > 0:
					state = token_stack[-1]
				# Check if char equals the last item on the stack
				if nextchar == state:
					token_stack.pop()
				# Add char to stack if it doesn't match
				else:
					token_stack.append(nextchar)

			# Add char to current token
			token += nextchar

		# If the loop has been terminated, but there are still elements left on the stack
		if len(token_stack) > 0:
			raise ValueError("Invalid string")
		# Safe to add final token to list of tokens
		elif len(token) > 0:
			tokens.append(token)

		return tokens

## Testing
shell = Shell(status = constants.SHELL_STATUS_STOP)
parser = Parser(shell)

print(parser.parse("echo '$test this is a test of something'"))
