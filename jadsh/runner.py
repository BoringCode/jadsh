import sys

import jadsh.constants as constants

class Runner:
	def __init__(self, stdin = sys.stdin, stdout = sys.stdout):
		self.stdin = stdin
		self.stdout = stdout

	def execute(self, tokens):
		return "result of command"