# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from .application import Application

# Initialize default app
# Only for use within *this* module.
# One should always call use_app() to obtain the default app.
default_app = None


def use_app(backend_name=None, call_reuse=True):
    """ Get/create the default Application object

    It is safe to call this function multiple times, as long as
    backend_name is None or matches the already selected backend.

    Parameters
    ----------
    backend_name : str | None
        The name of the backend application to use. If not specified, Vispy
        tries to select a backend automatically. See ``vispy.use()`` for
        details.
    call_reuse : bool
        Whether to call the backend's `reuse()` function (True by default).
        Not implemented by default, but some backends need it. For example,
        the notebook backends need to inject some JavaScript in a notebook as
        soon as `use_app()` is called.

    """
    global default_app

    # If we already have a default_app, raise error or return
    if default_app is not None:
        names = default_app.backend_name.lower().replace('(', ' ').strip(') ')
        names = [name for name in names.split(' ') if name]
        if backend_name and backend_name.lower() not in names:
            raise RuntimeError('Can only select a backend once, already using '
                               '%s.' % names)
        else:
            if call_reuse:
                default_app.reuse()
            return default_app  # Current backend matches backend_name

    # Create default app
    default_app = Application(backend_name)
    return default_app


def create():
    """Create the native application.
    """
    use_app(call_reuse=False)
    return default_app.create()


def run():
    """Enter the native GUI event loop.
    """
    use_app(call_reuse=False)
    return default_app.run()


def quit():
    """Quit the native GUI event loop.
    """
    use_app(call_reuse=False)
    return default_app.quit()


def process_events():
    """Process all pending GUI events

    If the mainloop is not running, this should be done regularly to
    keep the visualization interactive and to keep the event system going.
    """
    use_app(call_reuse=False)
    return default_app.process_events()
