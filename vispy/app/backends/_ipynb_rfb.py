import asyncio

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...app import Timer
from ._offscreen_util import OffscreenCanvasHelper


# todo: can create a global GL context helper here too

try:
    from jupyter_rfb import RemoteFrameBuffer
except Exception:
    RemoteFrameBuffer = object
    _msg = 'ipynb_rfb backend relies on a the jupyter_rfb library: ``pip install jupyter_rfb``'
    available, testable, why_not, which = False, False, _msg, None
else:
    available, testable, why_not = True, False, None
    which = "jupyter_rfb"


# try:
#     # Explicitly use default (avoid using test-app)
#     _app = Application('default')
# except Exception:
#     _msg = 'ipynb_rf backend relies on a proxy backend'
#     available, testable, why_not, which = False, False, _msg, None
# else:
#     # Try importing jupyter_rfb
#     # todo: give good error message if jupyter_rfb is not available
#     try:
#         from jupyter_rfb import RemoteFrameBuffer
#     except Exception as exp:
#         available, testable, why_not, which = False, False, str(exp), None
#     else:
#         available, testable, why_not = True, False, None
#         which = _app.backend_module.which


# -------------------------------------------------------------- capability ---

capability = dict(
    title=True,  # But it only applies to the dummy window :P
    size=True,
    position=False,
    show=True, # todo: can show/hide window?? -> should probably be false
    vsync=False,
    resizable=True,
    decorate=False,
    fullscreen=False,
    context=True,  # via the proxy backend
    multi_window=True,  # todo: right?
    scroll=True,
    parent=False,
    always_on_top=False,
)


# ------------------------------------------------------- set_configuration ---

# todo: call this?
def _set_config(c):
    _app.backend_module._set_config(c)


# ------------------------------------------------------------- application ---


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        super().__init__()
        # self._proxy_app_backend = _app._backend

    def _vispy_get_backend_name(self):
        # proxyname = self._proxy_app_backend._vispy_get_backend_name()
        # return f'ipynb_rfb (via {proxyname})'
        return f'ipynb_rfb'

    def _vispy_process_events(self):
        # return self._proxy_app_backend._vispy_process_events()
        raise RuntimeError("Cannot process events while asyncio event-loop is running.")

    def _vispy_run(self):
        pass  # We're in IPython; don't enter a mainloop or we'll block!

    def _vispy_quit(self):
        # return self._proxy_app_backend._vispy_quit()
        pass

    def _vispy_get_native_app(self):
        # return self._proxy_app_backend._vispy_get_native_app()
        return asyncio


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend, RemoteFrameBuffer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # todo: take stuff from kwargs, such as size
        # Get helper object to get a GL context and a FBO to render to
        self._helper = OffscreenCanvasHelper()
        self._helper.set_physical_size(640, 480)

        self._loop = asyncio.get_event_loop()
        self._draw_pending = False
        self._logical_size = 640, 480
        self._vispy_set_size(640, 480)
        self._initialized = False
        self._vispy_update()

    def receive_events(self, widget, content, buffers):
        return

        if content['msg_type'] == 'init':
            self.canvas_backend._reinit_widget()
        elif content['msg_type'] == 'events':
            events = content['contents']
            for ev in events:
                self.gen_event(ev)
        elif content['msg_type'] == 'status':
            if content['contents'] == 'removed':
                # Stop all timers associated to the widget.
                _stop_timers(self.canvas_backend._vispy_canvas)

    def on_draw(self):
        self._draw_pending = False
        # Handle initialization
        if not self._initialized:
            self._initialized = True
            self._vispy_canvas.events.initialize()
            physical_size = self._logical_size  # todo: physical != logical
            self._vispy_canvas.events.resize(
                size=self._logical_size,
                physical_size=physical_size,
             )

        # Normal behavior
        self._vispy_canvas.set_current()
        with self._helper:
            self._vispy_canvas.events.draw(region=None)

        # Present
        array = self._helper.get_frame()
        self._ndraws = getattr(self, "_ndraws", 0) + 1
        self.send_frame(array)

    def _vispy_warmup(self):
        self._vispy_canvas.set_current()

    def _vispy_set_current(self):
        self._helper.set_current()

    def _vispy_swap_buffers(self):
        pass

    def _vispy_set_title(self, title):
        pass

    def _vispy_set_size(self, w, h):
        self.css_width = f"{w}px"
        self.css_width = f"{h}px"

    def _vispy_set_position(self, x, y):
        pass

    def _vispy_set_visible(self, visible):
        pass  # todo: could implement this by minimizing it, I guess?
        raise NotImplementedError()

    def _vispy_set_fullscreen(self, fullscreen):
        raise NotImplementedError()

    def _vispy_update(self):
        if not self._draw_pending:
            self._draw_pending = True
            self._loop.call_later(0.01, self.on_draw)

    def _vispy_close(self):
        raise NotImplementedError()

    def _vispy_get_size(self):
        return self._logical_size

    def _vispy_get_position(self):
        return 0, 0

    def _vispy_get_fullscreen(self):
        return False


# ------------------------------------------------------------------- timer ---

# todo: test this
class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        super().__init__(vispy_timer)
        self._proxy_timer_backend = _app.backend_module.TimerBackend(vispy_timer)

    def _vispy_start(self, interval):
        return self._proxy_timer_backend._vispy_start(interval)

    def _vispy_stop(self):
        return self._proxy_timer_backend._vispy_stop()

    def _vispy_timeout(self):
        return self._proxy_timer_backend._vispy_timeout()

    def _vispy_get_native_timer(self):
        return self._proxy_timer_backend._vispy_get_native_timer()


# todo: Taken from ipython/_widget.py, but it seems a bit weird to me
def _stop_timers(canvas):
    """Stop all timers in a canvas."""
    for attr in dir(canvas):
        try:
            attr_obj = getattr(canvas, attr)
        except NotImplementedError:
            continue  # not everything is implemented in this backend
        if isinstance(attr_obj, Timer):
            attr_obj.stop()

