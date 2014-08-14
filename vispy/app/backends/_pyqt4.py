# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" PyQt4 proxy backend for the qt backend. 
"""

import sys
from .. import backends
from ...util import logger

try:
    # Try importing
    from PyQt4 import QtGui, QtCore, QtOpenGL  # noqa
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
else:
    # Success
    available, testable, why_not = True, True, None
    has_uic = True
    which = ('PyQt4', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)
    # Remove _qt module to force an import even if it was already imported
    sys.modules.pop(__name__.replace('_pyqt4', '_qt'), None)
    # Import _qt. Keep a ref to the module object!
    if backends.qt_lib is None:
        backends.qt_lib = 'pyqt4'  # Signal to _qt what it should import
        from . import _qt  # noqa
        from ._qt import *  # noqa
    else:
        logger.info('%s already imported, cannot switch to %s'
                    % (backends.qt_lib, 'pyqt4'))
