import sys
import os
import jadsh.constants as constants

class Prompt():
    def __init__(self, promptChar = "$"):
        self.promptChar = promptChar

    def draw(self):
        pwd = os.getcwd()
        sys.stdout.write(pwd + ":" + self.promptChar + ' ')
        sys.stdout.flush()

    def hilite(self, string, status = False, bold = False):
    	attr = []
    	if status:
    		# green
    		attr.append('32')
    	else:
    		# red
    		attr.append('31')
    	if bold:
    		attr.append('1')
    	return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
