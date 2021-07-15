"""
Utils for offscreen rendering.
"""

from .. import Application, Canvas
from ... import gloo


# todo: we can share the context accross multiple canvases / fbo's
# todo: how well does resizing an FBO work ... can we use just an fbo (no heper wrapper)


class OffscreenCanvasHelper:
    """ Provides a canvas to render to, using an FBO.
    """

    def __init__(self):
        self._fbo = None
        self._size = 1, 1
        self._get_context()

    def _get_context(self):

        try:
            import glfw
        except ImportError:
            self.glfw = None
        else:
            self.glfw = glfw

        if self.glfw:
            self.glfw.init()
            self.glfw.window_hint(self.glfw.VISIBLE, 0)
            self._canvas = self.glfw.create_window(1, 1, "dummy window", None, None)
        else:
            _app = Application('default')
            self._canvas = Canvas(app=_app)
            self._canvas.show(False)

    def set_current(self):
        if self.glfw:
            self.glfw.make_context_current(self._canvas)
        else:
            self._canvas._vispy_set_current()

        if self._fbo is None:
            self._create_fbo()

    def _create_fbo(self):
        w, h = self._size
        color_buffer = gloo.Texture2D((h, w, 4))
        depth_buffer = gloo.RenderBuffer((h, w))
        self._fbo = gloo.FrameBuffer(color_buffer, depth_buffer)

    def set_physical_size(self, w, h):
        new_size = w, h
        if new_size != self._size:
            self._size = new_size
            self._create_fbo()

    def __enter__(self):
        return self._fbo.__enter__()

    def __exit__(self, *args):
        return self._fbo.__exit__(*args)

    def get_frame(self):
        with self._fbo:
            return self._fbo.read()
