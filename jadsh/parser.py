import os, sys, re

from jadsh.runner import Runner
import jadsh.constants as constants

class Parser:
	"""A tokenizer that integrates with jadsh"""
	def __init__(self, runner = Runner()):
		# Reference to task runner
		self.runner = runner

		self.eof = None

		self.comments = "#"

		self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
		                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
		                  'ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
		                  'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')

		self.command_split = ';'
		self.whitespace = ' \t\r\n'
		self.quotes = '\'"'
		self.parens = "()"
		self.escape = '\\'

	def parse(self, instream):
		instream = str(instream).strip()

		# Check syntax before running through tokenizer
		# Will raise errors which must be caught
		self.check_syntax(instream)

		commands = self.read_tokens(instream)

		return commands

	def read_tokens(self, instream):
		commands = [[]]
		commands_index = 0
		token_stack = [] 
		token = ''

		quoted = False
		escaped = False
		substitution = False

		for nextchar in instream:
			# EOF
			if nextchar is self.eof:
				break

			# Ignore comments
			if nextchar in self.comments:
				break

			# Found a new command, increment
			# Don't increment the command if we are performing a command substitution or if we are inside a quote
			if nextchar == self.command_split and not quoted and not substitution and not escaped:
				commands[commands_index].append(self.expandVars(token))
				token = ''
				commands.append([])
				commands_index += 1
				continue

			# Syntax check to help users
			if not quoted and token == "&&":
				raise ValueError("Unsupported use of &&. In jadsh, please use 'COMMAND; and COMMAND'")

			# Split tokens on whitespace
			if nextchar in self.whitespace and len(token_stack) == 0:
				if len(token) > 0:
					commands[commands_index].append(self.expandVars(token))
					token = ''
				continue

			# Command substitution
			if nextchar in self.parens and not escaped and not quoted:
				state = None
				if len(token_stack) > 0:
					state = token_stack[-1]
				# Found matching paren, pop from the stack
				if state is not None and nextchar != state:
					token_stack.pop()
					# Reached the end of the paren group, recursively execute the token (this allows nesting commands)
					# Set the value of the current token equal to the stdout of the command
					if len(token_stack) == 0:
						commands_string = token
						token = ''
						for cmd in self.read_tokens(commands_string):
							output = self.runner.execute(cmd, True)
							if output["stdout"]:
								token += output["stdout"].read().decode("utf-8")
				# Add paren to token if the stack has parens in it already
				# This ensures that the paren is preserved if it is wrapped in parens already
				# Allows paren nesting
				if len(token_stack) != 0: token += nextchar
				# Add paren to stack
				if state is None or nextchar == state:
					token_stack.append(nextchar)
				substitution = len(token_stack) != 0
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
				elif state is None:
					token_stack.append(nextchar)
			
			# Should I escape the next character?
			escaped = nextchar == self.escape

			# Add char to current token
			token += nextchar


		# If the loop has been terminated, but there are still elements left on the stack
		if len(token_stack) > 0:
			raise ValueError("Unexpected end of string")
		# Safe to add final token to list of tokens
		elif len(token) > 0:
			commands[commands_index].append(self.expandVars(token))

		return commands

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

	def check_syntax(self, instream):
		"""
		Pre-check syntax before parsing tokens
		"""
		# Command substitution not supported
		if instream[0] in self.parens:
			raise ValueError("Illegal command name \"%s\"" % instream)

		if instream[0] == "$":
			raise ValueError("Unsupported use of $VARIABLE. In jadsh, variables cannot be used directly. Use 'eval $VARIABLE' instead.")

		return True

if __name__ == "__main__":
	parser = Parser()
	print(parser.parse("echo (pwd; whoami)"))