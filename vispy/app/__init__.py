""" 
The app module defines three classes: Application, Canvas, and Timer. 
On loading, vispy creates a default Application instance which can be used
via functions in the module's namespace.
"""

import vispy

from .application import Application, ApplicationBackend
from .canvas import Canvas, CanvasBackend
from .timer import Timer, TimerBackend

# Create default application instance
default_app = Application()


def use(backend_name):
    """ Select a backend by name. If the backend name is omitted,
    will chose a suitable backend automatically. It is an error to
    try to select a particular backend if one is already selected.
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
