# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""PySide2 proxy backend for the qt backend."""

import sys
from .. import backends
from ...util import logger
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')

try:
    # Try importing (QtOpenGL first to fail without import QtCore)
    if not USE_EGL:
        from PySide2 import QtOpenGL  # noqa
    from PySide2 import QtGui, QtCore  # noqa
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
else:
    # Success
    available, testable, why_not = True, True, None
    # What is this for? PyQt5 sets this to true, PySide sets this to false
    has_uic = False
    import PySide2

    # PySide2 doesn't have qWait for some reason see:
    # https://github.com/pyqtgraph/pyqtgraph/pull/376/commits/8bdc19be75a7552cc0043bf8b5f5e0ee796edda0
    from PySide2 import QtTest
    if not hasattr(QtTest.QTest, 'qWait'):
        @staticmethod
        def qWait(msec):
            import time
            start = time.time()
            PySide2.QtWidgets.QApplication.processEvents()
            while time.time() < start + msec * 0.001:
                PySide2.QtWidgets.QApplication.processEvents()
        QtTest.QTest.qWait = qWait

    which = ('PySide2', PySide2.__version__, QtCore.__version__)
    # Remove _qt module to force an import even if it was already imported
    sys.modules.pop(__name__.replace('_pyside2', '_qt'), None)
    # Import _qt. Keep a ref to the module object!
    if backends.qt_lib is None:
        backends.qt_lib = 'pyside2'  # Signal to _qt what it should import
        from . import _qt  # noqa
        from ._qt import *  # noqa
    else:
        logger.warning('%s already imported, cannot switch to %s'
                       % (backends.qt_lib, 'pyside2'))
