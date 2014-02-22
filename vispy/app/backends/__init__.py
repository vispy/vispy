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
BACKENDS = [('Qt', '_qt', None),  # Meta backend
            ('Pyglet', '_pyglet', 'pyglet'),
            ('PySide', '_qt', 'PySide'),
            ('PyQt4', '_qt', 'PyQt4'),
            ('Glfw', '_glfw', 'vispy.app.backends._libglfw'),
            ('Glut', '_glut', 'OpenGL.GLUT'),
            #('Test', 'nonexistent', 'foo.bar.lalalala'),  # For testing
            ]

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
BACKENDMAP = dict([(be[0].lower(), be) for be in BACKENDS])

# List of attempted backends. For logging and for communicating
# to the backends.
ATTEMPTED_BACKENDS = []


def has_qt(requires_uic=False, return_which=False):
    try:
        from PyQt4 import QtCore, QtGui, QtOpenGL, uic  # noqa
    except ImportError:
        has_uic = False
        try:
            from PySide import QtCore, QtGui, QtOpenGL  # noqa
        except ImportError:
            which = None
            has = False
        else:
            import PySide
            which = 'PySide ' + str(PySide.__version__)
            has = True
    else:
        which = 'PyQt4 ' + str(QtOpenGL.__file__)
        has = True
        has_uic = True

    if requires_uic:
        has = (has and has_uic)
    if return_which:
        out = (has, which)
    else:
        out = has
    return out


def has_pyglet(return_which=False):
    try:
        import pyglet  # noqa
    except:
        which = None
        has = False
        pass
    else:
        has = True
        which = 'pyglet ' + str(pyglet.version)
    if return_which:
        out = (has, which)
    else:
        out = has
    return out


def has_glfw(return_why=False, return_which=False):
    try:
        from . import _glfw  # noqa
    except Exception as exp:
        has = False
        which = None
        why = str(exp)
        pass
    else:
        has = True
        which = 'glfw ' + str(_glfw.glfw.__version__)
        why = ''
    if return_why:
        if return_which:
            out = (has, why, which)
        else:
            out = (has, why)
    else:
        if return_which:
            out = (has, which)
        else:
            out = has
    return out


def has_glut(return_which=False):
    try:
        from OpenGL import GLUT  # noqa
    except:
        has = False
        which = None
    else:
        import OpenGL
        has = True
        which = 'from OpenGL %s' % OpenGL.__version__
    if return_which:
        out = (has, which)
    else:
        out = has
    return out


def requires_qt(requires_uic=False):
    extra = ' with UIC' if requires_uic else ''
    return np.testing.dec.skipif(not has_qt(requires_uic),
                                 'Requires QT' + extra)


def requires_pyglet():
    return np.testing.dec.skipif(not has_pyglet(), 'Requires Pyglet')


def requires_glfw():
    has, why = has_glfw(return_why=True)
    return np.testing.dec.skipif(not has, 'Requires Glfw: %s' % why)


def requires_non_glut():
    return np.testing.dec.skipif(not has_pyglet() and not has_qt(),
                                 'Requires non-Glut backend')
