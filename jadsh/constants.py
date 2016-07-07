VERSION = 0.2

PYTHON_VERSION = "3.5"

SHELL_STATUS_RUN = 1
SHELL_STATUS_STOP = 0

import re
VARIABLE_PATTERN = re.compile("([$][A-Za-z])\w+")

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))