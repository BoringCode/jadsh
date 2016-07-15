VERSION = "0.2.0"

PYTHON_VERSION = "3.5"

HELP_URL = "https://github.com/BoringCode/jadsh/wiki"

SHELL_STATUS_RUN = 1
SHELL_STATUS_STOP = 0

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Keyboard
KEY_NULL = 0       # NULL
CTRL_C = 3         # Ctrl-c
CTRL_D = 4         # Ctrl-d
CTRL_F = 6         # Ctrl-f
CTRL_H = 8         # Ctrl-h
TAB = 9            # Tab
NEWLINE = 10 	   # \n
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
CTRL_ARROW_LEFT = 1010
CTRL_ARROW_RIGHT = 1011
CTRL_ARROW_UP = 1012
CTRL_ARROW_DOWN = 1013