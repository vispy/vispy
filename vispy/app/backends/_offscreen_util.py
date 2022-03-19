"""
Utils for offscreen rendering.
"""

from .. import Application, Canvas
from ... import gloo


class OffscreenContext:
    """ A helper class to provide an OpenGL context. This context is global
    to the application.
    """

    _global_instance = None
    _canvas = None

    @classmethod
    def get_global_instance(cls):
        """ Get a global context. Note that any assumptions about OpenGL state
        being local will not hold.
        """
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance

    def __init__(self):
        if self._canvas is not None:
            return  # already initialized

        self._is_closed = False

        # Glfw is probably the most lightweight approach, so let's try that.
        # But there are two incompatible packages providing glfw :/
        self.glfw = None
        try:
            import glfw
        except ImportError:
            pass
        else:
            need_from_glfw = ["create_window", "make_context_current"]
            if all(hasattr(glfw, attr) for attr in need_from_glfw):
                self.glfw = glfw

        if self.glfw:
            self.glfw.init()
            self.glfw.window_hint(self.glfw.VISIBLE, 0)
            self._canvas = self.glfw.create_window(1, 1, "dummy window", None, None)
        else:
            try:
                _app = Application('default')
            except Exception:
                raise RuntimeError(
                    "Cannot find a backend to create an OpenGL context. "
                    "Install e.g. PyQt5, PySide2, or `pip install glfw`."
                )
            self._canvas = Canvas(app=_app)
            self._canvas.show(False)

    def make_current(self):
        """ Make this the currently active context.
        """
        # If an application only used off-screen canvases this would technically
        # have to be called just once. But note that an application/session
        # could run both real canvases and off-screen ones.
        if self.glfw:
            self.glfw.make_context_current(self._canvas)
        else:
            self._canvas.set_current()

    def close(self):
        """ Close the context. """
        # Cannot close the global instance
        if self is OffscreenContext._global_instance:
            return
        elif not self._is_closed:
            self._is_closed = True
            if self.glfw:
                self.glfw.destroy_window(self._canvas)
            else:
                self._canvas.close()

    def __del__(self):
        self.close()


class FrameBufferHelper:
    """ Provides a canvas to render to, using an FBO.
    """

    def __init__(self):
        self._fbo = None
        self._physical_size = 1, 1
        self._fbo_size = -1, -1

    def _ensure_fbo(self):
        if self._fbo_size != self._physical_size:
            self._fbo_size = self._physical_size
            w, h = self._fbo_size
            if self._fbo is None:
                color_buffer = gloo.Texture2D((h, w, 4))
                depth_buffer = gloo.RenderBuffer((h, w))
                self._fbo = gloo.FrameBuffer(color_buffer, depth_buffer)
            else:
                self._fbo.resize((h, w))

    def set_physical_size(self, w, h):
        """ Set the physical size of the canvas.
        """
        self._physical_size = w, h

    def get_frame(self):
        """ Call this within the with-context to obtain the frame buffer contents.
        """
        return self._fbo.read()

    def __enter__(self):
        self._ensure_fbo()
        return self._fbo.__enter__()

    def __exit__(self, *args):
        return self._fbo.__exit__(*args)
