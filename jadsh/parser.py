import os, sys, re

from jadsh.runner import Runner
import jadsh.constants as constants

class Parser:
	"""
	A tokenizer that integrates with jadsh
	This class handles parsing string input according to the jadsh syntax
	Supports command expansions and comments
	"""
	def __init__(self, runner = Runner()):
		# Reference to task runner
		self.runner = runner

		# Line comments are ignored by the tokenizer
		self.comments = "#"

		self.command_split = ';'
		self.whitespace = ' \t\r\n'
		self.quotes = '\'"'
		self.parens = "()"
		self.escape = '\\'

	def __call__(self, instream):
		"""
		Calling the class directly will redirect to the parse function
		"""
		return self.parse(instream)

	def parse(self, instream):
		"""
		Helper function to pass string to read_tokens() method
		"""
		# Remove all surrounding whitespace from string
		instream = str(instream).strip()

		commands = self.read_tokens(instream)

		return commands

	def read_tokens(self, instream):
		"""
		Takes an input string and returns a list of tokenized commands
		"""
		commands = []
		tokens = []
		token_stack = [] 
		token = ''

		quoted = False
		escaped = False
		substitution = False

		# Check syntax before running through tokenizer
		# Will raise errors which must be caught
		if not self.check_syntax(instream): return commands

		for nextchar in instream:
			# EOF
			if nextchar is None:
				break

			# Ignore comments
			if nextchar in self.comments:
				break

			# Found a new command, increment
			# Don't increment the command if we are performing a command substitution or if we are inside a quote
			if nextchar == self.command_split and not quoted and not substitution and not escaped:
				tokens.append(token)
				commands.append(tokens)
				token = ''
				tokens = []
				continue

			# Syntax check to help users
			if not quoted and token == "&&":
				raise ValueError("Unsupported use of &&. In jadsh, please use `COMMAND; and COMMAND`")
			elif not quoted and token == "||":
				raise ValueError("Unsupported use of ||. In jadsh, please use `COMMAND; or COMMAND`")

			# Split tokens on whitespace
			if nextchar in self.whitespace and len(token_stack) == 0:
				if len(token) > 0:
					tokens.append(token)
					token = ''
				continue

			# Command substitution
			if nextchar in self.parens and not escaped and not quoted:
				state = None
				# Create substitution string that will be passed to task runner
				if substitution is False:
					substitution_string = ''
				if len(token_stack) > 0:
					state = token_stack[-1]
				# Found matching paren, pop from the stack
				if state is not None and nextchar != state:
					token_stack.pop()
					# Reached the end of the paren group, recursively execute the token (this allows nesting commands)
					# Set the value of the current token equal to the stdout of the command
					if len(token_stack) == 0:
						for cmd in self.read_tokens(substitution_string):
							output = self.runner(cmd, True)
							if output["stdout"]:
								token += output["stdout"].read().decode("utf-8")
								output["stdout"].close()
				# Add paren to token if the stack has parens in it already
				# This ensures that the paren is preserved if it is wrapped in parens already
				# Allows paren nesting
				if len(token_stack) != 0: substitution_string += nextchar
				# Add paren to stack
				if state is None or nextchar == state:
					token_stack.append(nextchar)
				substitution = len(token_stack) != 0
				continue

			# Quotes
			if nextchar in self.quotes and not escaped:
				state = None
				# Check if stack has characters on it
				if len(token_stack) > 0:
					state = token_stack[-1]
				# Check if char equals the last item on the stack
				if nextchar == state:
					token_stack.pop()
					quoted = len(token_stack) != 0
				# Add char to stack if it doesn't match
				elif state is None:
					quoted = True
					token_stack.append(nextchar)
			
			# Should I escape the next character?
			escaped = nextchar == self.escape

			# Add char to substitution string
			if substitution:
				substitution_string = substitution_string + nextchar
			# Append char to token if we aren't creating a command substitution
			else:
				token = token + nextchar

		# If the loop has been terminated, but there are still elements left on the stack
		if len(token_stack) > 0:
			raise ValueError("Unexpected end of string")
		# Safely add final token to list of tokens
		elif len(token) > 0:
			tokens.append(token)
			commands.append(tokens)

		return commands

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