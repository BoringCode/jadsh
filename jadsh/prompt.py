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
