VERSION = 0.2

PYTHON_VERSION = "3.5"

SHELL_STATUS_RUN = 1
SHELL_STATUS_STOP = 0

import re
VARIABLE_PATTERN = re.compile("([$][A-Za-z])\w+")

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Keyboard
KEY_NULL = 0       # NULL
CTRL_C = 3         # Ctrl-c
CTRL_D = 4         # Ctrl-d
CTRL_F = 6         # Ctrl-f
CTRL_H = 8         # Ctrl-h
TAB = 9            # Tab
CTRL_L = 12        # Ctrl+l
ENTER = 13         # Enter
CTRL_Q = 17        # Ctrl-q
CTRL_S = 19        # Ctrl-s
CTRL_U = 21        # Ctrl-u
ESC = 27           # Escape
BACKSPACE =  127   # Backspace
# Soft codes, not reported by terminal directly
ARROW_UP = 1000
ARROW_DOWN = 1001
ARROW_RIGHT = 1002
ARROW_LEFT = 1003
HOME_KEY = 1004
END_KEY = 1005
PAGE_UP = 1006
PAGE_DOWN = 1007
DEL_KEY = 1008