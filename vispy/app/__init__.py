# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" 
The app module defines three classes: Application, Canvas, and Timer. 
On loading, vispy creates a default Application instance which can be used
via functions in the module's namespace.
"""

from __future__ import print_function, division, absolute_import

import vispy

from .application import Application, ApplicationBackend
from .canvas import Canvas, CanvasBackend
from .timer import Timer, TimerBackend

# Create default application instance
default_app = Application()


def use(backend_name=None):
    """ Select a backend by name. If the backend name is omitted, will
    chose a suitable backend automatically. It is an error to try to
    select a particular backend if one is already selected. Available
    backends: 'PySide', 'PyQt4', 'Glut', 'Pyglet', 'qt'. The latter
    will use PySide or PyQt4, whichever works.
    
    If a backend name is provided, and that backend could not be loaded,
    an error is raised.
    
    If no backend name is provided, this function will first check if
    the GUI toolkit corresponding to each backend is already imported,
    and try that backend first. If this is unsuccessful, it will try
    the 'default_backend' provided in the vispy config. If still not
    succesful, it will try each backend in a predetermined order.
    """
    return default_app.use(backend_name)


def run():
    """ Enter the native GUI event loop. 
    """
    return default_app.run()


def quit(self):
    """ Quit the native GUI event loop.
    """
    return default_app.quit()


def process_events(self):
    """ Process all pending GUI events. If the mainloop is not
    running, this should be done regularly to keep the visualization
    interactive and to keep the event system going.
    """
    return default_app.process_events()
