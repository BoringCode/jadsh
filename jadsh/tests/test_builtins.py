import unittest, getpass, socket, os
from jadsh.tests import BaseShellTest

# Python2.7 does not have the module I need
try:
	from tempfile import TemporaryDirectory
except:
	from legacy_support import TemporaryDirectory

class cdTest(BaseShellTest):
	def test_default_behavior(self):
		self.runCommand("cd")

		home = os.environ.get("HOME")

		output = self.runCommand("pwd")

		self.assertEqual(output[-2], home, "cd should by default go to $HOME")

	def test_cd_with_args(self):
		with TemporaryDirectory() as temp_dir:
			self.runCommand("cd " + temp_dir)

			output = self.runCommand("pwd")

			self.assertEqual(output[-2], temp_dir, "cd should change directory when passed a single arg")

	def test_previous_directory(self):
		initial_dir = self.runCommand("pwd")[-2]

		with TemporaryDirectory() as temp_dir:
			self.runCommand("cd " + temp_dir)

			self.runCommand("cd -")

			output = self.runCommand("pwd")

			self.assertEqual(output[-2], initial_dir, "cd should change to previous directory when passed arg `-`")

	def test_invalid_directory(self):
		invalid_directory = "/fake"
		error_message = "cd: The directory \"%s\" does not exist" % invalid_directory

		output = self.runCommand("cd " + invalid_directory)

		self.assertTrue(error_message in output, "cd should display error when changing to invalid directory")

	def test_help_text(self):
		output = self.runCommand("cd --help")

		expected_value = "cd -- change directory"

		self.assertTrue(expected_value in output, "cd --help should output help text")

class exportTest(BaseShellTest):
	def test_default_behavior(self):
		output = self.runCommand("export")

		variable_present = True		
		for key in os.environ:
			variable_present = (str(key) + " " + str(os.getenv(key))).strip() in output
			if not variable_present:
				break

		self.assertTrue(variable_present, "export should display list of environment key/value pairs")

	def test_assign_value(self):
		variable_name = self.randomString(5)
		variable_value = self.randomString(10)

		self.runCommand("export %s=%s" % (variable_name, variable_value))

		output = self.runCommand("echo $" + variable_name)

		self.assertEqual(output[-2], variable_value, "export should export new variable to environment")

	def test_multiple_values(self):
		values = {
			self.randomString(5): self.randomString(20),
			self.randomString(20): "",
			self.randomString(10): '"%s %s %s"' % (self.randomString(5), self.randomString(20), self.randomString(10))
		}

		command = "export"
		for key in values:
			command += " %s=%s" % (key, values[key])
		self.runCommand(command)

		for key in values:
			self.assertEqual(values[key].strip('"\''), self.runCommand("echo $%s" % key)[-2], "export should export new variable to environment ($%s = %s)" % (key, values[key]))

	def test_invalid_variable(self):
		error_message = "export error: Can't export variables to environment"
		variable_name = ".-dkjfd"
		variable_value = self.randomString(10)

		output = self.runCommand("export %s=%s" % (variable_name, variable_value))
		self.assertTrue(error_message in output, "export should only accept alphabet characters in variable")

		output = self.runCommand("export " + self.randomString(20))
		self.assertTrue(error_message in output, "export should do nothing with invalid input")

	def test_help(self):
		help_message = "Usage: `export VARIABLE=value`"

		output = self.runCommand("export --help")

		self.assertTrue(help_message in output, "export --help should display help message")

class andTest(BaseShellTest):
	def test_good_prior_command(self):
		pwd = os.getcwd()
		output = self.runCommand("ls; and pwd")

		self.assertEqual(pwd, output[-2], "`and` should run the command if the previous command was successful")

	def test_bad_prior_command(self):
		pwd = os.getcwd()
		bad_command = self.randomString(20)

		output = self.runCommand("%s; and pwd" % bad_command)

		self.assertFalse(pwd in output, "`and` shouldn't run the command if the previous command failed")

	def test_help(self):
		help_message = "and -- conditionally execute a command"

		output = self.runCommand("and --help")

		self.assertTrue(help_message in output, "and --help should display help message")

class orTest(BaseShellTest):
	def test_good_prior_command(self):
		pwd = os.getcwd()
		output = self.runCommand("ls; or pwd")

		self.assertFalse(pwd in output, "`or` shouldn't run the command if the previous command was successful")

	def test_bad_prior_command(self):
		pwd = os.getcwd()
		bad_command = self.randomString(20)

		output = self.runCommand("%s; or pwd" % bad_command)

		self.assertEqual(pwd, output[-2], "`or` should run the command if the previous command failed")

	def test_help(self):
		help_message = "or -- conditionally execute a command"

		output = self.runCommand("or --help")

		self.assertTrue(help_message in output, "or --help should display help message")

if __name__ == '__main__':
	unittest.main()