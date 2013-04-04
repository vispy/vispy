# -*- coding: utf-8 -*-
# Copyright (c) 2013, Almar Klein
# (new) BSD License.

"""
This __init__ module enables importing a package from its repository
source. The usual layout of a package's source code in the repository
is something like:

+ root_dir
  + package_name  
    __init__.py
    ...
  + docs
  setup.py

To be able to import the package:
  * place this file in root_dir
  * place root_dir somewhere on the PYTHONPATH
  * name root_dir equal to package_name 

""" 

import os
import sys

# Determine directory and package name
THISDIR = os.path.abspath(os.path.dirname(__file__))
THISPACKAGENAME = os.path.basename(THISDIR)

# Insert in sys.path, so we can import the *real* package
if not THISDIR in sys.path:
    sys.path.insert(0, THISDIR)

# Remove *this* module from sys.modules, so we can import that name again
# (keep reference to avoid premature cleanup)
_old = sys.modules.pop(THISPACKAGENAME, None)

# Import the *real* package. This will put the new package in
# sys.modules. Note that the new package is injected in the namespace
# from which "import package" is called; we do not need to import *.
__import__(THISPACKAGENAME, level=0)

# Clean up after ourselves
if THISDIR in sys.path:
    sys.path.remove(THISDIR)
