import os
from jadsh.constants import *

def cd(args):
    os.chdir(args[0])
    return SHELL_STATUS_RUN
