# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import sys
import platform
from os import path as op
import traceback
import tempfile
import atexit
from shutil import rmtree

from ._logging import use_log_level, logger


###############################################################################
# System info

def sys_info(fname=None, overwrite=False):
    """Get relevant system and debugging information

    Parameters
    ----------
    fname : str | None
        Filename to dump info to. Use None to simply print.
    overwrite : bool
        If True, overwrite file (if it exists).

    Returns
    -------
    out : str
        The system information as a string.
    """
    if fname is not None and op.isfile(fname) and not overwrite:
        raise IOError('file exists, use overwrite=True to overwrite')

    out = ''
    try:
        # Nest all imports here to avoid any circular imports
        from ..app import Application, Canvas, backends
        from ..gloo import gl
        # get default app
        this_app = Application()
        with use_log_level('warning'):
            this_app.use()  # suppress unnecessary messages
        out += 'Platform: %s\n' % platform.platform()
        out += 'Python:   %s\n' % str(sys.version).replace('\n', ' ')
        out += 'Backend:  %s\n' % this_app.backend_name
        out += 'Qt:       %s\n' % backends.has_qt(return_which=True)[1]
        out += 'Pyglet:   %s\n' % backends.has_pyglet(return_which=True)[1]
        out += 'glfw:     %s\n' % backends.has_glfw(return_which=True)[1]
        out += 'glut:     %s\n' % backends.has_glut(return_which=True)[1]
        out += '\n'
        # We need an OpenGL context to get GL info
        if 'glut' in this_app.backend_name.lower():
            # glut causes problems
            out += 'OpenGL information omitted for glut backend\n'
        else:
            canvas = Canvas('Test', (10, 10), show=False, app=this_app)
            canvas._backend._vispy_set_current()
            out += 'GL version:  %s\n' % gl.glGetParameter(gl.GL_VERSION)
            x_ = gl.GL_MAX_TEXTURE_SIZE
            out += 'MAX_TEXTURE_SIZE: %d\n' % gl.glGetParameter(x_)
            out += 'Extensions: %s\n' % gl.glGetParameter(gl.GL_EXTENSIONS)
            canvas.close()
    except Exception:  # don't stop printing info
        out += '\nInfo-gathering error:\n%s' % traceback.format_exc()
        pass
    if fname is not None:
        with open(fname, 'w') as fid:
            fid.write(out)
    return out


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
# Testing helpers


class app_opengl_context(object):
    """Context manager that provides an active OpenGL context"""

    # This method mostly wraps to set_log_level, but also takes
    # care of enabling/disabling message recording in the formatter.
    def __init__(self, backend=None):
        self.backend = backend
        self.c = None
        self._callback = None
        self._callback_error = None
        self._callback_result = None

    def __enter__(self):
        from .. import app  # nest to avoid circular imports

        # Create app
        self.app = app.Application()
        self.app.use(self.backend)
        self.app.create()

        # Create canvas
        self.c = app.Canvas(size=(300, 200), autoswap=False, app=self.app)
        self.c.events.paint.connect(self._on_paint)
        self.c.show()

        # Create timer
        self.timer = app.Timer(0.1, app=self.app, iterations=1)
        self.timer.connect(self._on_timer)

        # Make sure we are initialized, painted, etc.
        if self.backend == 'qt':
            # pyglet gets stuck
            for i in range(1):
                self.paint()
        return self

    def _on_paint(self, event):
        self._paintflag = True
        self._callback_result = None
        if self._callback is not None:
            try:
                self._callback_result = self._callback()
            except Exception as err:
                self._callback_error = err

    def _on_timer(self, event):
        self._timerflag = True

    def paint(self, callback=None):
        """ Run a callback in a paint event, then return result or
        raise error.
        """
        # Prepare
        self._callback = callback
        self._callback_error = None
        self._paintflag = False
        # Force redraw and wait for it to finish
        self.c.update()
        while not self._paintflag:
            self.app.process_events()
        # Raise if there was an error
        if self._callback_error is not None:
            raise self._callback_error
        return self._callback_result

    def test(self, callback=None, n=1):
        """ Run a callback in a paint event, but try at most n times.
        If one try went well, all is well. This is necessary because
        readpixels sometimes produces bogus one or two times during
        warmup or something.
        """
        for iter in range(n):
            try:
                res = self.paint(callback)
                if iter > 0:
                    print('it took %i tests' % (iter+1))
                return res  # if success, we return
            except Exception:
                pass
        else:
            raise self._callback_error

    def wait(self):
        """ Wait a tiny bit for the event loop.
        """
        self._timerflag = False
        self.timer.start()
        while not self._timerflag:
            self.app.process_events()

    def __exit__(self, type, value, traceback):
        if self.backend == 'qt':
            self.wait()
        try:
            self.c.close()
        except Exception:
            logger.warn('Failed to close canvas')
        return


class _TempDir(str):
    """Class for creating and auto-destroying temp dir

    This is designed to be used with testing modules.

    We cannot simply use __del__() method for cleanup here because the rmtree
    function may be cleaned up before this object, so we use the atexit module
    instead.
    """
    def __new__(self):
        new = str.__new__(self, tempfile.mkdtemp())
        return new

    def __init__(self):
        self._path = self.__str__()
        atexit.register(self.cleanup)

    def cleanup(self):
        rmtree(self._path, ignore_errors=True)
