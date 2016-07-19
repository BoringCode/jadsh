import os, re, sys, subprocess, importlib
import jadsh.constants as constants

class Runner:
	"""
	Task runner for jadsh
	This class handles executing programs and builtins
	"""
	def __init__(self, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr

		self.builtins = {}
		# Some builtins have odd names to account for Python keywords (e.g. _and)
		self.builtin_prefixes = ['', '_']

		self.ignore_status = ["and", "or"]

	def __call__(self, tokens, return_output = False):
		"""
		Direct calls are passed to the execute function
		"""
		return self.execute(tokens, return_output)

	def execute(self, tokens, return_output = False):
		"""
		Execute tokens and return status code of command
		"""
		# No tokens, return status of 0
		if len(tokens) == 0: 
			return {
				"stdout": None,
				"status": 0,
				"builtin": False
			}

		if return_output: 
			stdout = subprocess.PIPE
		else:
			stdout = self.stdout

		# Expand variables at execution time
		tokens = [ self.cleanToken(self.expandVars(token)) for token in tokens ]
		command = tokens[0]
		args = tokens[1:]

		# Check if builtin command
		if self.builtin(command):
			try:
				process = self.builtins[command].execute(*args)
			except Exception as e:
				self.message("%s error" % command, str(e))
			obj = {
				"stdout": process["stdout"] if "stdout" in process else None,
				"status": process["returncode"] if "returncode" in process else None,
				"builtin": True
			}
		else:
			# Open command as a subprocess
			process = subprocess.Popen(tokens, stdin = self.stdin, stdout = stdout, stderr = self.stderr)
			# Block program execution until process is finished
			process.wait()
			obj = {
				"stdout": process.stdout,
				"status": process.returncode,
				"builtin": False
			}
		if not command in self.ignore_status:
			# Export status to environment
			os.environ["status"] = str(obj["status"])
		return obj

	def expandVars(self, path, default=None, skip_escaped=True, skip_single_quotes = True):
		"""
		Expand environment variables of form $var and ${var}.
		If parameter 'skip_escaped' is True, all escaped variable references (i.e. preceded by backslashes) are skipped.
		Unknown variables are set to 'default'. If 'default' is None, they are left unchanged.
		"""
		# Don't expand vars in single quoted strings
		if len(path) == 0 or (skip_single_quotes and (path[0] == "'" and path[-1] == "'")): return path

		def replace_var(m):
		    return os.environ.get(m.group(2) or m.group(1), m.group(0) if default is None else default)

		reVar = (r'(?<!\\)' if skip_escaped else '') + r'\$(\w+|\{([^}]*)\})'
		string = re.sub(reVar, replace_var, path)
		return string

	def cleanToken(self, token):
		"""
		Remove wrapping quotation marks and other elements from token
		"""
		if len(token) == 0: return token
		quotes = "'\""
		if len(token) > 1 and token[0] in quotes and token[-1] in quotes:
			token = token[1:-1]
		token = token.replace("\\", "")
		return token

	def builtin(self, command):
		"""
		Check if a command is a builtin

		@return Boolean (is a builtin or not)
		"""
		# Check if the command has already been loaded as a builtin
		if command in self.builtins: return True
		for prefix in self.builtin_prefixes:
			try:
			    # Attempt to load this command as a module. If it doesn't exist, the function will return false
			    mod = importlib.import_module("jadsh.builtins.%s" % command)
			    # Generate new builtin object (passing this shell as an argument)
			    obj = getattr(mod, prefix + command)(self.stdin, self.stdout, self.stderr)
			    self.builtins[command] = obj
			    return True
			except ImportError:
				return False
			except:
				continue
		return False


