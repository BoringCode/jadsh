import sys
from jadsh.constants import *

class Prompt():

    def __init__(self, promptChar = "$"):
        self.promptChar = promptChar

    def draw(self):
        sys.stdout.write(self.promptChar + ' ')
        sys.stdout.flush()
