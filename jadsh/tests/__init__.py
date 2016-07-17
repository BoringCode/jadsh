import unittest
import os, sys, tempfile, time, random, string
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
		if self.shell.exitcode is None:
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
		return self.cleanOutput(self.stdin.readlines())

	def cleanOutput(self, output):
		for i in range(len(output)):
			output[i] = output[i].strip()
		return output

	def getcwd(self):
		home = os.path.expanduser("~")
		pwd = os.getcwd()
		pwd = pwd.replace(home, "~")
		return pwd

	def randomString(self, length, numbers = False):
		choices = string.ascii_uppercase
		if numbers:
			choices += string.digits
		return ''.join(random.SystemRandom().choice(choices) for _ in range(length))