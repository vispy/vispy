# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from . import Application, Canvas, Timer


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
        self.c = Canvas(size=(300, 200), autoswap=False, app=self.app)
        self.c.events.paint.connect(self._on_paint)
        self.c.show()
        self.c._warmup()

        # Create timer
        self.timer = Timer(0.1, app=self.app, iterations=1)
        self.timer.connect(self._on_timer)
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
        self.app.process_events()
        if not self._paintflag:
            raise RuntimeError('app framework error, not painted')
        # Raise if there was an error
        if self._callback_error is not None:
            raise self._callback_error
        return self._callback_result

    def test(self, callback=None, n=5):
        """ Run a callback in a paint event, but try at most n times.
        If one try went well, all is well. This is necessary because
        readpixels sometimes produces bogus one or two times during
        warmup or something.
        """
        try:
            res = self.paint(callback)
        except Exception:
            raise self._callback_error
        else:
            return res  # if success, we return

    def __exit__(self, type, value, traceback):
        self.c.close()
        return
