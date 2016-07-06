import sys
import os
from subprocess import check_output
from jadsh.constants import *

class Prompt():

    def __init__(self, promptChar = "$"):
        self.promptChar = promptChar

    def draw(self):
        pwd = check_output(["pwd"])[:-1]
        sys.stdout.write(pwd + self.promptChar + ' ')
        sys.stdout.flush()
