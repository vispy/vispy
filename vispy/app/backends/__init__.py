# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""vispy.app.backends

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
    ('PyQt6', '_pyqt6', 'PyQt6'),
    ('PySide', '_pyside', 'PySide'),
    ('PySide2', '_pyside2', 'PySide2'),
    ('PySide6', '_pyside6', 'PySide6'),
    ('Pyglet', '_pyglet', 'pyglet'),
    ('Glfw', '_glfw', 'vispy.ext.glfw'),
    ('SDL2', '_sdl2', 'sdl2'),
    ('wx', '_wx', 'wx'),
    ('EGL', '_egl', 'vispy.ext.egl'),
    ('osmesa', '_osmesa', 'vispy.ext.osmesa'),
    ('tkinter', '_tk', 'tkinter'),
]

# Whereas core backends really represents libraries that can create a
# canvas, the pseudo backends act more like a proxy.
PSEUDO_BACKENDS = [
    ('jupyter_rfb', '_jupyter_rfb', None),
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

# Flag for _pyside, _pyside2 _pyqt4 and _qt modules to communicate.
qt_lib = None
