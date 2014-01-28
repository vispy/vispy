# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.app.backends

The backend modules are dynamically imported when needed. This module
defines a small description of each supported backend, so that for
instance we can test whether the GUI toolkit for a backend is already
imported. This stuff is mostly used in the Application.use method.
"""

import numpy as np

# Define backends: name, vispy.app.backends.xxx module, native module name.
# This is the order in which they are attempted to be imported.
BACKENDS = [('Test', 'nonexistent', 'foo.bar.lalalala'),  # For testing
            ('Qt', '_qt', None),  # Meta backend
            ('Pyglet', '_pyglet', 'pyglet'),
            ('PySide', '_qt', 'PySide'),
            ('PyQt4', '_qt', 'PyQt4'),
            ('Glut', '_glut', 'OpenGL.GLUT'),
            ]

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
BACKENDMAP = dict([(be[0].lower(), be) for be in BACKENDS])

# List of attempted backends. For logging and for communicating
# to the backends.
ATTEMPTED_BACKENDS = []


def has_qt(requires_uic=False):
    try:
        from PyQt4 import QtCore, QtGui, QtOpenGL, uic  # noqa
    except ImportError:
        has_uic = False
        try:
            from PySide import QtCore, QtGui, QtOpenGL  # noqa
        except ImportError:
            has = False
        else:
            has = True
    else:
        has = True
        has_uic = True

    if requires_uic:
        has = (has and has_uic)
    return has


def has_pyglet():
    try:
        import pyglet  # noqa
        has = True
    except:
        has = False
        pass
    return has


def requires_qt(requires_uic=False):
    extra = ' with UIC' if requires_uic else ''
    return np.testing.dec.skipif(not has_qt(requires_uic),
                                 'Requires QT' + extra)


def requires_pyglet():
    return np.testing.dec.skipif(not has_pyglet(), 'Requires Pyglet')


def requires_non_glut():
    return np.testing.dec.skipif(not has_pyglet() and not has_qt(),
                                 'Requires non-Glut backend')
