# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from . import Application, Canvas


class app_opengl_context(object):
    """ Context manager that provides an active OpenGL context

    Used mostly for testing or taking screenshots.
    """

    # This method mostly wraps to set_log_level, but also takes
    # care of enabling/disabling message recording in the formatter.
    def __init__(self, backend=None):
        self.backend = backend
        self.c = None
        self._callback = None
        self._callback_error = None
        self._callback_result = None

    def __enter__(self):
        # Create app
        self.app = Application()
        self.app.use(self.backend)
        self.app.create()

        # Create canvas
        self.c = Canvas(size=(300, 200), autoswap=False, app=self.app,
                        show=True, title='test app')
        self.c._backend._vispy_warmup()
        return self

    def test(self, callback=None, show=False):
        """ Run a callback in a paint event """
        out = callback()
        from vispy.gloo import gl
        gl.glFinish()
        return out

    def __exit__(self, type, value, traceback):
        self.c.close()
