import unittest, getpass, socket, os
from jadsh.tests import BaseShellTest
import jadsh.constants

class ShellTest(BaseShellTest):
	def test_startup(self):
		"""
		On startup, the shell should display a welcome message and the prompt
		"""
		expected_value = [
			"Welcome to jadsh, Just Another Dumb SHell", 
			"Type help for instructions on how to use jadsh",
			self.getPrompt()
		]

		welcome = self.getOutput()

		self.assertEqual(welcome, expected_value, "Welcome message does not appear")

	def test_exit(self):
		output = self.runCommand("exit")

		exit_message = "Bye!"
		self.assertEqual(output[-1], exit_message, "Shell should exit with 'Bye!' message")

		exit_code = 0
		self.assertEqual(self.shell.exitcode, exit_code, "Shell should exit with a status of 0")

	def test_exit_ctrl_d(self):
		exit_message = "Bye!"
		exit_code = 0
		ctrl_d = chr(jadsh.constants.CTRL_D)

		output = self.runCommand(ctrl_d)[-1]

		self.assertEqual(output, exit_message, "CTRL-D should cause shell to exit with 'Bye!' message")
		self.assertEqual(self.shell.exitcode, exit_code, "Shell should exit with status of 0")

	def test_backspace(self):
		command = self.randomString(20)
		backspace = chr(jadsh.constants.BACKSPACE)

		self.stdout.write(command)
		self.stdout.flush()

		self.stdout.write(backspace)
		self.stdout.flush()

		expected_value = self.getPrompt() + " " + command[:-1]

		self.assertEqual(self.getOutput()[-1], expected_value, "Backspace should remove one character from shell input")

	def test_clear_input(self):
		ctrl_c = chr(jadsh.constants.CTRL_C)

		self.stdout.write(self.randomString(20))
		self.stdout.flush()

		self.stdout.write(ctrl_c)
		self.stdout.flush()

		expected_value = self.getPrompt()

		self.assertEqual(self.getOutput()[-1], expected_value, "CTRL-C should clear the shell input")

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

	def test_command_substitution_chaining(self):
		username = getpass.getuser()
		pwd = os.getcwd()

		output = self.runCommand("echo (pwd; whoami)")

		self.assertTrue(pwd in output and username in output, "Shell should chain commands in command substitutions")

	def test_chain_commands(self):
		username = getpass.getuser()
		pwd = os.getcwd()

		output = self.runCommand("whoami; pwd")

		self.assertTrue(username in output and pwd in output, "Shell should allow chaining commands with `;`")

	def test_invalid_commands(self):
		invalid_command = self.randomString(20, True)
		error_message = invalid_command + ": command not found"

		output = self.runCommand(invalid_command)[-2]

		self.assertEqual(output, error_message, "Shell should output error on invalid command")

if __name__ == '__main__':
	unittest.main()