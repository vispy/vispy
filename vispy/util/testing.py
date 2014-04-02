# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np


###############################################################################
# Adapted from Python's unittest2 (which is wrapped by nose)
# http://docs.python.org/2/license.html

def _safe_rep(obj, short=False):
    """Helper for assert_* ports"""
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < 80:
        return result
    return result[:80] + ' [truncated]...'


def _safe_str(obj):
    """Helper for assert_* ports"""
    try:
        return str(obj)
    except Exception:
        return object.__str__(obj)


def _format_msg(msg, std_msg):
    """Helper for assert_* ports"""
    if msg is None:
        msg = std_msg
    else:
        try:
            msg = '%s : %s' % (std_msg, msg)
        except UnicodeDecodeError:
            msg = '%s : %s' % (_safe_str(std_msg), _safe_str(msg))
    return msg


def assert_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member in container:
        return
    std_msg = '%s not found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_not_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member not in container:
        return
    std_msg = '%s found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_is(expr1, expr2, msg=None):
    """Backport for old nose.tools"""
    if expr1 is not expr2:
        std_msg = '%s is not %s' % (_safe_rep(expr1), _safe_rep(expr2))
        raise AssertionError(_format_msg(msg, std_msg))


###############################################################################
# GL stuff

def _has_pyopengl():
    try:
        from OpenGL import GL  # noqa
    except Exception:
        return False
    else:
        return True


def requires_pyopengl():
    return np.testing.dec.skipif(not _has_pyopengl(), 'Requires PyOpenGL')


###############################################################################
# App stuff

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
        which = ('PyQt4 ' + QtCore.PYQT_VERSION_STR +
                 ' Qt ' + QtCore.QT_VERSION_STR)
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
        from ..app.backends import _pyglet  # noqa
    except Exception:
        which = None
        has = False
    else:
        has = True
        which = 'pyglet ' + str(_pyglet.version)
    if return_which:
        out = (has, which)
    else:
        out = has
    return out


def has_glfw(return_why=False, return_which=False):
    try:
        from ..app.backends import _glfw  # noqa
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
    except Exception:
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


def requires_glut():
    return np.testing.dec.skipif(not has_glut(), 'Requires Glut')


def requires_application():
    return np.testing.dec.skipif(not any([has_pyglet(), has_qt(),
                                          has_glfw(), has_glut()]),
                                 'Requires application backend')
