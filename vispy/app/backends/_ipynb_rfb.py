import asyncio

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...app import Timer
from ...util import keys
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

    _double_click_supported = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # Init
        self._helper = OffscreenCanvasHelper()
        self._loop = asyncio.get_event_loop()
        self._draw_pending = False
        self._logical_size = 1, 1
        self._physical_size = 1, 1
        self._initialized = False
        # Init more based on kwargs (could maybe handle, title, show, context)
        self._vispy_set_size(*kwargs["size"])
        self.resizable = kwargs["resizable"]
        # Need a first update
        self._vispy_update()

    def receive_event(self, ev):
        type = ev["event_type"]
        if type == "resize":
            # Note that jupyter_rfb already throttles this event
            w, h, r = ev["width"], ev["height"], ev["pixel_ratio"]
            self._logical_size = w, h
            self._physical_size = int(w * r), int(h * r)
            self._loop.call_soon(self._emit_resize_event)
        elif type == "pointer_down":
            with self._helper:
                self._vispy_mouse_press(
                    native=ev,
                    pos=(ev["x"], ev["y"]),
                    button=ev["button"],
                    modifiers=self._modifiers(ev),
                )
        elif type == "pointer_up":
            self._vispy_mouse_release(
                native=ev,
                pos=(ev["x"], ev["y"]),
                button=ev["button"],
                modifiers=self._modifiers(ev),
            )
        elif type == "pointer_move":
            self._vispy_mouse_move(
                native=ev,
                pos=(ev["x"], ev["y"]),
                button=ev["button"],
                modifiers=self._modifiers(ev),
            )
        elif type == "double_click":
            self._vispy_mouse_double_click(
                native=ev,
                pos=(ev["x"], ev["y"]),
                button=ev["button"],
                modifiers=self._modifiers(ev),
            )
        elif type == "wheel":
            self._vispy_canvas.events.mouse_wheel(native=ev,
                pos=(ev["x"], ev["y"]),
                delta=(ev["dx"] / 100, - ev["dy"] / 100),
                modifiers=self._modifiers(ev),
            )
        elif type == "key_down":
            # The special key names are all (most?) the same
            # But the key is actually more like tex, e.g. shift + 3 becomes "#"
            self._vispy_canvas.events.key_press(
                native=ev,
                key=keys.Key(ev["key"]),
                modifiers=self._modifiers(ev),
                text=ev["key"],
            )
        elif type == "key_up":
            self._vispy_canvas.events.key_release(
                native=ev,
                key=keys.Key(ev["key"]),
                modifiers=self._modifiers(ev),
                text=ev["key"],
            )
        elif type == "close-todo":
            _stop_timers(self._vispy_canvas)
        else:
            pass  # event ignored / unknown

    def _modifiers(self, ev):
        return tuple(getattr(keys, m.upper()) for m in ev["modifiers"])

    def _emit_resize_event(self):
        self._helper.set_physical_size(*self._physical_size)
        self._vispy_canvas.events.resize(
            size=self._logical_size,
            physical_size=self._physical_size,
            )

    def on_draw(self):
        self._draw_pending = False
        # Handle initialization
        if not self._initialized:
            self._initialized = True
            self._vispy_canvas.events.initialize()
            self._emit_resize_event()

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
        self.css_height = f"{h}px"

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

    def _vispy_get_physical_size(self):
        return self._physical_size

    def _vispy_get_position(self):
        return 0, 0

    def _vispy_get_fullscreen(self):
        return False


# ------------------------------------------------------------------- timer ---

# note (AK): in ipython/widget.py there is a function that sop
class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        super().__init__(vispy_timer)
        self._loop = asyncio.get_event_loop()
        self._task = None

    async def _timer_coro(self, interval):
        while True:
            await asyncio.sleep(interval)
            self._vispy_timeout()

    def _vispy_start(self, interval):
        if self._task is not None:
            self._task.cancel()
        self._task = asyncio.create_task(self._timer_coro(interval))

    def _vispy_stop(self):
        self._task.cancel()
        self._task = None

    def _vispy_timeout(self):
        self._loop.call_soon(self._vispy_timer._timeout)


def _stop_timers(canvas):
    """Stop all timers associated with a canvas."""
    for attr in dir(canvas):
        try:
            attr_obj = getattr(canvas, attr)
        except NotImplementedError:
            continue  # prevent error due to props that we don't implement
        else:
            if isinstance(attr_obj, Timer):
                attr_obj.stop()
