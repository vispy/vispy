import pyvis

from .application import Application, ApplicationBackend
from .canvas import Canvas, CanvasBackend
from .timer import Timer, TimerBackend

# Create default application instance
default_app = Application()


def use(backend_name):
    return default_app.use(backend_name)


def run():
    return default_app.run()

