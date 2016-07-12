import sys, os, socket, getpass
import jadsh.constants as constants

class Prompt():
    def __init__(self, promptChar = "$"):
    	self.home = os.path.expanduser("~")
    	self.promptChar = promptChar

    def generate(self):
        pwd = self.getcwd()
        return self.title("jadsh " + os.getcwd()) + getpass.getuser() + "@" + socket.gethostname() + ":" + pwd + ":" + self.promptChar + ' '

    def getcwd(self):
    	pwd = os.getcwd()
    	pwd = pwd.replace(self.home, "~")
    	return pwd

    def title(self, title = "jadsh"): 
    	return "\x1b]2;" + title + "\x07"

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
