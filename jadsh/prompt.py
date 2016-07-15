import os, socket, getpass
import jadsh.constants as constants

class Prompt():
    def __init__(self, promptChar = "$"):
        self.home = os.path.expanduser("~")
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.promptChar = promptChar

    def generate(self):
        pwd = self.getcwd()
        return self.username + "@" + self.hostname + ":" + pwd + ":" + self.promptChar + ' '

    def getcwd(self):
    	pwd = os.getcwd()
    	pwd = pwd.replace(self.home, "~")
    	return pwd

    def title(self, title = "jadsh"):
        return "\x1b]2;" + title + "\x07"
