import pyvis

from .canvas import Canvas, CanvasBackend
from .app import App, AppBackend

app = App()

# todo: dont we want the app instance to be in pyvis.app?
