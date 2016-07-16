import unittest, getpass, socket
from jadsh.tests import BaseShellTest

class ShellTest(BaseShellTest):
	def test_startup(self):
		"""
		On startup, the shell should display a welcome message and the prompt
		"""
		username = getpass.getuser()
		hostname = socket.gethostname()

		expected_value = [
			"Welcome to jadsh, Just Another Dumb SHell", 
			"Type help for instructions on how to use jadsh",
			username + "@" + hostname + ":" + self.getcwd() + ":$"
		]

		welcome = self.getOutput()

		self.assertEqual(welcome, expected_value, "Welcome message does not appear")

	def test_exit(self):
		output = self.runCommand("exit")

		exit_message = "Bye!"
		self.assertEqual(output[-1], exit_message, "Shell should exit with 'Bye!' message")

		exit_code = 0
		self.assertEqual(self.shell.exitcode, exit_code, "Shell should exit with a status of 0")


if __name__ == '__main__':
	unittest.main()