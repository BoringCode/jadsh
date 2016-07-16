import unittest
import os, getpass, socket, sys, tempfile, time
from multiprocessing import Process

from jadsh.shell import Shell

class BaseShellTest(unittest.TestCase):
	def setUp(self):
		# One way communication to child process
		childStdin, parentStdout = os.pipe()

		# Open file descriptor for manipulation
		self.stdout = os.fdopen(parentStdout, "w")

		# One way communication from the child process
		self.stdin = self.tempFile("r+")

		# Create new shell process (passing in stdin and stdout for the child process)
		self.shell = Process(target=self.createShell, args=(childStdin, self.stdin, ))
		self.shell.start()

	def createShell(self, childStdin, stdout):
		stdin = os.fdopen(childStdin, "r")
		shell = Shell(stdin = stdin, stdout = stdout)
		stdin.close()

	def tearDown(self):
		# Safely exit the shell
		self.runCommand("exit")
		# Wait for shell to exit before continuing
		self.shell.join()
		# Close file descriptors
		self.stdin.close()
		self.stdout.close()
		# Delete temp file
		os.unlink(self.stdin.name)

	def tempFile(self, permissions):
		# Generate new temporary file and return a file object
		(file_descriptor, file_name) = tempfile.mkstemp()
		os.close(file_descriptor)
		return open(file_name, permissions)

	def runCommand(self, command):
		# Pass command to the shell
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