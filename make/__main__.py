
from __future__ import print_function, division

import os
import sys
from make import Maker

START_DIR = os.path.abspath(os.getcwd())

try:
    Maker(sys.argv)
finally:
    os.chdir(START_DIR)
