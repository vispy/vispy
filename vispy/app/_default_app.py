# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from .application import Application

default_app = Application()


def use(backend_name=None):
    """Select a backend by name

    Parameters
    ----------
    name : str | None
        If None (default), a suitable backend will be chosen automatically.
        It is an error to try to select a particular backend if one is
        already selected. Available backends:
        'PySide', 'PyQt4', 'Glut', 'Pyglet', 'qt'. 'qt' will use PySide
        or PyQt4, whichever works.

    Notes
    -----
    If a backend name is provided, and that backend could not be loaded,
    an error is raised.

    If no backend name is provided, this function will first check if
    the GUI toolkit corresponding to each backend is already imported,
    and try that backend first. If this is unsuccessful, it will try
    the 'default_backend' provided in the vispy config. If still not
    succesful, it will try each backend in a predetermined order.
    """
    return default_app.use(backend_name)


def create():
    """Create the native application.
    """
    return default_app.create()


def run():
    """Enter the native GUI event loop.
    """
    return default_app.run()


def quit():
    """Quit the native GUI event loop.
    """
    return default_app.quit()


def process_events():
    """Process all pending GUI events

    If the mainloop is not running, this should be done regularly to
    keep the visualization interactive and to keep the event system going.
    """
    return default_app.process_events()
