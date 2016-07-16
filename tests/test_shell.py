import unittest
import os, getpass, socket, sys, tempfile, time
from inspect import *

from multiprocessing import Process, Pipe

from jadsh.shell import Shell

def createShell(childStdin, stdout):
	stdin = os.fdopen(childStdin, "r")
	shell = Shell(stdin = stdin, stdout = stdout)
	stdin.close()

class BaseShellTest(unittest.TestCase):
	def setUp(self):
		childStdin, parentStdout = os.pipe()

		# Significantly easier to read a file, than with a pipe
		self.stdin = self.tempFile("r+")

		# Communicate with the shell via a pipe
		self.stdout = os.fdopen(parentStdout, "w")

		self.shell = Process(target=createShell, args=(childStdin, self.stdin, ))
		self.shell.start()

	def tearDown(self):
		# Safely exit the shell
		self.runCommand("exit")
		# Wait for shell to exit before continuing
		self.shell.join()
		self.stdin.close()
		self.stdout.close()
		# Delete temp file
		os.unlink(self.stdin.name)

	def tempFile(self, permissions):
		(file_descriptor, file_name) = tempfile.mkstemp()
		os.close(file_descriptor)
		return open(file_name, permissions)

	def runCommand(self, command):
		self.stdout.write(str(command) + "\n")
		self.stdout.flush()
		return self.getOutput()

	def getOutput(self, pause = 0.1):
		# Slightly hacky way to make sure the shell is finished with its job before grabbing output
		time.sleep(pause)
		self.stdin.seek(0)
		return self.stdin.readlines()

	def getcwd(self):
		home = os.path.expanduser("~")
		pwd = os.getcwd()
		pwd = pwd.replace(home, "~")
		return pwd

class StartupTest(BaseShellTest):
	def test_startup(self):
		"""
		On startup, the shell should display a welcome message and the prompt
		"""
		username = getpass.getuser()
		hostname = socket.gethostname()

		expected_value = "Welcome to jadsh, Just Another Dumb SHell\n"
		expected_value += "Type help for instructions on how to use jadsh\n"
		expected_value += username + "@" + hostname + ":" + self.getcwd() + ":$ \n"

		welcome = ''.join(self.getOutput())

		self.assertEqual(welcome, expected_value, "Welcome message does not appear")

if __name__ == '__main__':
	unittest.main()