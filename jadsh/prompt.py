import os, socket, getpass
import jadsh.constants as constants

class Prompt():
    def __init__(self, promptChar = "$"):
        self.pwd = self.getcwd()
        self.home = os.path.expanduser("~")
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.promptChar = promptChar

    def generate(self):
        pwd = self.getcwd()
        return "%s@%s:%s:%s " % (self.username, self.hostname, pwd, self.promptChar)

    def getcwd(self):
        try:
            self.pwd = os.getcwd()
            self.pwd = self.pwd.replace(self.home, "~")
        except:
            pass
        return self.pwd
