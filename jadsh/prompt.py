import sys
import os
from jadsh.constants import *

class Prompt():

    def __init__(self, promptChar = "$"):
        self.promptChar = promptChar

    def draw(self):
        pwd = os.getcwd()
        sys.stdout.write(pwd + ":" + self.promptChar + ' ')
        sys.stdout.flush()
