import sys
from jadsh.shell import Shell
import jadsh.constants as constants

def main(args = None):
	"""
	Launches a new instance of the shell
	"""

	if args is None:
		args = sys.argv[1:]

	# Parse arguments
	if "--version" in args or "-v" in args:
		print(constants.VERSION)
		return

	shell = Shell()

if __name__ == "__main__":
    main()