# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" PySide proxy backend for the qt backend. 
"""

import sys

# Check what libs are already imported
_loaded_pyqt4 = sys.modules.get('PyQt4.QtCore', None)
_loaded_pyside = sys.modules.get('PySide.QtCore', None)

try:
    if _loaded_pyqt4:
        raise RuntimeError('Cannot use PySide backend if PyQt4 is imported.')
    from PySide import QtGui, QtCore, QtOpenGL  # noqa

except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

else:
    # Right before importing this module, 'pyside' is added to
    # ATTEMPTED_BACKENDS so that _qt knows it should import PySide.
    from ._qt import *  # noqa
