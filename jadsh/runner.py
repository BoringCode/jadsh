import os, re, sys, subprocess, importlib
import jadsh.constants as constants

class Runner:
	def __init__(self, stdin = sys.stdin, stdout = sys.stdout):
		self.stdin = stdin
		self.stdout = stdout

		self.builtins = {}

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
		tokens = [ self.expandVars(token) for token in tokens ]
		command = tokens[0]
		args = tokens[1:]

		# Check if builtin command
		if self.builtin(command):
			process = self.builtins[command].execute(*args)
			obj = {
				"stdout": process["stdout"] if "stdout" in process else None,
				"status": process["returncode"] if "returncode" in process else None,
				"builtin": True
			}
		else:
			# Open command as a subprocess
			process = subprocess.Popen(tokens, stdin = self.stdin, stdout = stdout)
			# Block program execution until process is finished
			process.wait()
			obj = {
				"stdout": process.stdout,
				"status": process.returncode,
				"builtin": False
			}
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
		return string.replace("\\", "")

	def builtin(self, command):
		"""
		Check if a command is a builtin

		@return Boolean (is a builtin or not)
		"""
		# Check if the command has already been loaded as a builtin
		if command in self.builtins: return True
		try:
		    # Attempt to load this command as a module. If it doesn't exist, the function will return false
		    mod = importlib.import_module("jadsh.builtins." + command)
		    # Generate new builtin object (passing this shell as an argument)
		    obj = getattr(mod, command)(self.stdin, self.stdout)
		    self.builtins[command] = obj
		    return True
		except ImportError:
		    return False


