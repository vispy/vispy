# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import sys

# Check what libs are already imported
_loaded_pyqt4 = sys.modules.get('PyQt4.QtCore', None)
_loaded_pyside = sys.modules.get('PySide.QtCore', None)

try:
    if _loaded_pyside:
        raise RuntimeError('Cannot use PyQt4 backend if PySide is imported.')
    from PyQt4 import QtGui, QtCore, QtOpenGL
    
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

    class _QGLWidget(object):
        pass
    
    _QTimer = _QGLWidget

else:
    from ._qt import *
