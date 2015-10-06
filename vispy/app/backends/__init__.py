# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.app.backends

The backend modules are dynamically imported when needed. This module
defines a small description of each supported backend, so that for
instance we can test whether the GUI toolkit for a backend is already
imported. This stuff is mostly used in the Application.use method.
"""

# Define backends: name, vispy.app.backends.xxx module, native module name.
# This is the order in which they are attempted to be imported.
CORE_BACKENDS = [
    ('PyQt4', '_pyqt4', 'PyQt4'),
    ('PyQt5', '_pyqt5', 'PyQt5'),
    ('PySide', '_pyside', 'PySide'),
    ('Pyglet', '_pyglet', 'pyglet'),
    ('Glfw', '_glfw', 'vispy.ext.glfw'),
    ('SDL2', '_sdl2', 'sdl2'),
    ('wx', '_wx', 'wx'),
    ('EGL', '_egl', 'vispy.ext.egl'),
    ('osmesa', '_osmesa', 'vispy.ext.osmesa'),
]

# Whereas core backends really represents libraries that can create a
# canvas, the pseudo backends act more like a proxy.
PSEUDO_BACKENDS = [
    # ('ipynb_vnc', '_ipynb_vnc', None),
    # ('ipynb_static', '_ipynb_static', None),
    ('ipynb_webgl', '_ipynb_webgl', None),
    ('_test', '_test', 'vispy.app.backends._test'),  # add one that will fail
]

# Combine
BACKENDS = CORE_BACKENDS + PSEUDO_BACKENDS

# Get list of backend names
BACKEND_NAMES = [b[0].lower() for b in BACKENDS]

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
BACKENDMAP = dict([(be[0].lower(), be) for be in BACKENDS])

# List of attempted backends. For logging.
TRIED_BACKENDS = []

# Flag for _pyside, _pyqt4 and _qt modules to communicate.
qt_lib = None
