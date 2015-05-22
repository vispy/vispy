# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" PyQt5 proxy backend for the qt backend. 
"""

import sys
from .. import backends
from ...util import logger
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')

try:
    # Make sure no conflicting libraries have been imported.
    for lib in ['PySide', 'PyQt4']:
        lib += '.QtCore'
        if lib in sys.modules:
            raise RuntimeError("Refusing to import PyQt5 because %s is "
                               "already imported." % lib)
    # Try importing (QtOpenGL first to fail without import QtCore)
    if not USE_EGL:
        from PyQt5 import QtOpenGL  # noqa
    from PyQt5 import QtGui, QtCore  # noqa
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
else:
    # Success
    available, testable, why_not = True, True, None
    has_uic = True
    which = ('PyQt5', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)
    # Remove _qt module to force an import even if it was already imported
    sys.modules.pop(__name__.replace('_pyqt5', '_qt'), None)
    # Import _qt. Keep a ref to the module object!
    if backends.qt_lib is None:
        backends.qt_lib = 'pyqt5'  # Signal to _qt what it should import
        from . import _qt  # noqa
        from ._qt import *  # noqa
    else:
        logger.info('%s already imported, cannot switch to %s'
                    % (backends.qt_lib, 'pyqt5'))
