# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.app.backends

The backend modules are dynamically imported when needed. This module
defines a small description of each supported backend, so that for
instance we can test whether the GUI toolkit for a backend is already
imported. This stuff is mostly used in the Application.use method.
"""

# Define backends: name, vispy.app.backends.xxx module, native module name.
# This is the order in which they are attempted to be imported.
BACKENDS = [
    ('Qt', '_qt', None),  # Meta backend
    ('PySide', '_qt', 'PySide'),
    ('PyQt4', '_qt', 'PyQt4'),
    ('Pyglet', '_pyglet', 'pyglet'),
    ('Glfw', '_glfw', 'vispy.app.backends._libglfw'),
    ('SDL2', '_sdl2', 'sdl2'),
    ('Glut', '_glut', 'OpenGL.GLUT'),
]

BACKEND_NAMES = []
for backend in BACKENDS:
    if backend[1][1:] not in BACKEND_NAMES:  # remove redundant qt entries
        BACKEND_NAMES.append(backend[1][1:])

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
BACKENDMAP = dict([(be[0].lower(), be) for be in BACKENDS])

# List of attempted backends. For logging and for communicating
# to the backends.
ATTEMPTED_BACKENDS = []
