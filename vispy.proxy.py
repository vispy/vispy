# -*- coding: utf-8 -*-
# Copyright (c) 2013, Almar Klein
# (new) BSD License.

"""
This module provides an easy way to enable importing a package event
if it's not on sys.path. The main use case is to import a package 
from its developmment repository without having to install it.

This module is sort of like a symlink for Python modules.

To install: 
  1) Copy this file to a directory that is on the PYTHONPATH
  2) Rename the file to "yourpackage.py".

If the real package is in "yourpackage/yourpackage" relative to this file, 
you're done. Otherwise modify PARENT_DIR_OF_MODULE.

""" 

import os
import sys

# Determine directory and package name
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
MODULE_NAME = __name__

# Override if necessary
PARENT_DIR_OF_MODULE = os.path.join(THIS_DIR, MODULE_NAME)


# Insert in sys.path, so we can import the *real* package
if not PARENT_DIR_OF_MODULE in sys.path:
    sys.path.insert(0, PARENT_DIR_OF_MODULE)

# Remove *this* module from sys.modules, so we can import that name again
# (keep reference to avoid premature cleanup)
_old = sys.modules.pop(MODULE_NAME, None)

# Import the *real* package. This will put the new package in
# sys.modules. Note that the new package is injected in the namespace
# from which "import package" is called; we do not need to import *.
try:
  __import__(MODULE_NAME, level=0)
except Exception as err:
  sys.modules[MODULE_NAME] = _old  # Prevent KeyError
  raise


# Clean up after ourselves
if PARENT_DIR_OF_MODULE in sys.path:
    sys.path.remove(PARENT_DIR_OF_MODULE)
