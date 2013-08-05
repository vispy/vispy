# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.app.backends

The backend modules are dynamically imported when needed. This module
defines a small description of each supported backend, so that for
instance we can test whether the GUI toolkit for a backend is already
imported. This stuff is mostly used in the Application.use method.
"""

# Define backends: name, vispy.app.backends.xxx module, native module name.
# This is the order in which they are attempted to be imported.
BACKENDS = [    ('Test', 'nonexistent', 'foo.bar.lalalala'), # For testing
                ('Qt', 'qt', None),  # Meta backend
                ('Glut', 'glut', 'OpenGL.GLUT'),
                ('Pyglet', 'pyglet', 'pyglet'),
                ('PySide', 'qt', 'PySide'),
                ('PyQt4', 'qt', 'PyQt4'),
            ]

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
BACKENDMAP = dict([(be[0].lower(), be) for be in BACKENDS])

# List of attempted backends. For logging and for communicating to the backends.
ATTEMPTED_BACKENDS = []
