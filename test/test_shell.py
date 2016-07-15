import unittest
import os, getpass, socket, sys, tempfile, time
from inspect import *

from jadsh.shell import Shell

class BaseShellTest(unittest.TestCase):
	def setUp(self):
		self.files = []
		self.stdin = self.tempFile()
		self.stdout = self.tempFile()

		# Execute all commands that are listed in the doc string
		commands = getdoc(getattr(self, self._testMethodName))
		if commands:
			self.stdin.write(commands + "\nexit\n")
			self.stdin.seek(0)

		self.shell = Shell(stdin = self.stdin, stdout = self.stdout)

	def tearDown(self):
		for file in self.files:
			os.unlink(file)

	def tempFile(self):
		(file_descriptor, file_name) = tempfile.mkstemp()
		self.files.append(file_name)
		return open(file_name, "rw+")

	def readStdout(self, seekPosition = 0):
		self.stdout.seek(seekPosition)
		return self.stdout.readlines()

	def findString(self, string):
		valid = False
		for line in self.readStdout():
			if string in line:
				valid = True
				break
		return valid

	def getcwd(self):
		home = os.path.expanduser("~")
		pwd = os.getcwd()
		pwd = pwd.replace(home, "~")
		return pwd

class StartupTest(BaseShellTest):
	def test_startup(self):
		username = getpass.getuser()
		hostname = socket.gethostname()

		expected_value = "Welcome to jadsh, Just Another Dumb SHell\n"
		expected_value += "Type help for instructions on how to use jadsh\n"
		expected_value += username + "@" + hostname + ":" + self.getcwd() + ":$ \n"

		welcome = ''.join(self.readStdout())

		self.assertEqual(welcome, expected_value, "Welcome message does not appear")

class cdTest(BaseShellTest):
	def test_cd_no_args(self):
		"""
		cd /
		cd
		"""
		self.assertEqual(os.getenv("HOME"), os.getcwd(), "cd with no args should go to $HOME")

	def test_cd_args(self):
		"""
		cd /
		cd /etc/
		"""
		self.assertEqual("/etc", os.getcwd(), "cd with args should change directory to first arg")

	def test_cd_help(self):
		"""
		cd --help
		"""
		helpText = "cd -- change directory"
		self.assertTrue(self.findString(helpText))

if __name__ == '__main__':
	unittest.main()