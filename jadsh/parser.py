import os, sys, re
from io import StringIO

from jadsh.shell import Shell
from jadsh.runner import Runner
import jadsh.constants as constants

class Parser:
	"""A tokenizer that integrates with jadsh"""
	def __init__(self):
		self.runner = Runner()

		self.eof = None

		self.comments = "#"

		self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
		                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
		                  'ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
		                  'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')

		self.whitespace = ' \t\r\n'
		self.quotes = '\'"'
		self.parens = "()"
		self.escape = '\\'

	def parse(self, instream = None):
		if isinstance(instream, str):
			instream = StringIO(instream)

		if instream is None:
			instream = sys.stdin

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
		quoted = False
		escaped = False

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
				tokens.append(self.expandVars(token))
				token = ''
				continue

			# Quotes
			if nextchar in self.quotes and not escaped:
				state = None
				quoted = True
				# Check if stack has characters on it
				if len(token_stack) > 0:
					state = token_stack[-1]
				# Check if char equals the last item on the stack
				if nextchar == state:
					token_stack.pop()
					if len(token_stack) == 0: quoted = False
				# Add char to stack if it doesn't match
				else:
					token_stack.append(nextchar)

			# Should I escape the next character?
			escaped = nextchar == self.escape

			# Add char to current token
			token += nextchar

		# If the loop has been terminated, but there are still elements left on the stack
		if len(token_stack) > 0:
			raise ValueError("Invalid string")
		# Safe to add final token to list of tokens
		elif len(token) > 0:
			tokens.append(self.expandVars(token))

		return tokens

	def expandVars(self, path, default=None, skip_escaped=True, skip_single_quotes = True):
		"""
		Expand environment variables of form $var and ${var}.
		If parameter 'skip_escaped' is True, all escaped variable references (i.e. preceded by backslashes) are skipped.
		Unknown variables are set to 'default'. If 'default' is None, they are left unchanged.
		"""
		# Don't expand vars in single quoted strings
		if len(path) == 0 or (skip_single_quotes and (path[0] == "'" and path[-1] == "'")): return path

		def replace_var(m):
		    return os.environ.get(m.group(2) or m.group(1), m.group(0) if default is None else default)

		reVar = (r'(?<!\\)' if skip_escaped else '') + r'\$(\w+|\{([^}]*)\})'
		return re.sub(reVar, replace_var, path)

## Testing
parser = Parser()

print(parser.parse("echo $HOME"))
