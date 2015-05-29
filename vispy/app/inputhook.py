# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Support for interactive mode to allow VisPy's event loop to be run alongside
a console terminal, without using threads.  This code relies on inputhooks
built-in to the Python interpreter, and supports IPython too. The underlying
inputhook implementation is from IPython 3.x.

Note that IPython notebook integration is not supported, as the browser does
not use Python's PyOS_InputHook functionality.
"""

from ..ext.ipy_inputhook import inputhook_manager, InputHookBase, stdin_ready

from time import sleep
from ..util.ptime import time


def set_interactive(enabled=True, app=None):
    """Activate the IPython hook for VisPy.  If the app is not specified, the
    default is used.
    """
    if enabled:
        inputhook_manager.enable_gui('vispy', app)
    else:
        inputhook_manager.disable_gui()


@inputhook_manager.register('vispy')
class VisPyInputHook(InputHookBase):
    """Implementation of an IPython 3.x InputHook for VisPy.  This is loaded
    by default when you call vispy.app.run() in a console-based interactive
    session, but you can also trigger it manually by importing this module
    then typing:
        >>> %enable_gui vispy
    """

    def enable(self, app=None):
        """Activate event loop integration with this VisPy application.

        Parameters
        ----------
        app : instance of Application
           The VisPy application that's being used.  If None, then the
           default application is retrieved.

        Notes
        -----
        This methods sets the ``PyOS_InputHook`` to this implementation,
        which allows Vispy to integrate with terminal-based applications
        running in interactive mode (Python or IPython).
        """

        from .. import app as _app

        self.app = app or _app.use_app()
        self.manager.set_inputhook(self._vispy_inputhook)
        return app

    def _vispy_inputhook(self):
        try:
            while not stdin_ready():
                self.app.process_events()

                # refer https://github.com/vispy/vispy/issues/945 for more context
                # we need to wait out on the event loop to prevent CPU stress
                # but not wait too much, to maintain fluidity.
                # if Qt is available, we choose to use Qt's qWait that automatically
                # guarantees that it will wait for 0.05 seconds maximum, while
                # ensuring responsiveness

                if self.app.backend_name == "PyQt4":
                    import PyQt4.QtTest

                    PyQt4.QtTest.QTest.qWait(5)  # in ms

                elif self.app.backend_name == "PyQt5":
                    import PyQt5.QtTest

                    PyQt5.QtTest.QTest.qWait(5)  # in ms

                else:
                    sleep(0.005)  # in s

        except KeyboardInterrupt:
            pass
        return 0
