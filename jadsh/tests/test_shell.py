import unittest, getpass, socket, os
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

	def test_command_execution(self):
		output = self.runCommand("whoami")

		username = getpass.getuser()

		self.assertEqual(output[-2], username, "Whoami should execute and return current username")

	def test_variable_expansion(self):
		home = os.getenv("HOME")
		output = self.runCommand("echo $HOME")[-2]

		self.assertEqual(output, home, "Shell should expand variables in commands")

		output = self.runCommand("echo \$HOME")[-2]
		self.assertEqual("$HOME", output, "Shell should escape variables in commands")

	def test_chain_commands(self):
		username = getpass.getuser()
		pwd = os.getcwd()

		output = self.runCommand("whoami; pwd")

		self.assertTrue(username in output and pwd in output, "Shell should allow chaining commands with `;`")

if __name__ == '__main__':
	unittest.main()