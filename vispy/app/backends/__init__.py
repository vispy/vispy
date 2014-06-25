# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.app.backends

The backend modules are dynamically imported when needed. This module
defines a small description of each supported backend, so that for
instance we can test whether the GUI toolkit for a backend is already
imported. This stuff is mostly used in the Application.use method.
"""

# Import names from vispy.util. Names are defined there to avoid having
# to copy the names.
from ...util._use import (APP_BACKENDS as BACKENDS,  # noqa
                          APP_BACKEND_NAMES as BACKEND_NAMES,  # noqa
                          APP_BACKENDMAP as BACKENDMAP)  # noqa

# List of attempted backends. For logging.
ATTEMPTED_BACKENDS = []

# Flag for _pyside, _pyqt4 and _qt modules to communicate.
qt_lib = None
