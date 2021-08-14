import asyncio

from ..base import BaseApplicationBackend, BaseCanvasBackend, BaseTimerBackend
from ...app import Timer
from ...util import keys
from ._offscreen_util import OffscreenContext, FrameBufferHelper


try:
    from jupyter_rfb import RemoteFrameBuffer
except Exception:
    RemoteFrameBuffer = object
    _msg = 'The jupyter_rfb backend relies on a the jupyter_rfb library: ``pip install jupyter_rfb``'
    available, testable, why_not, which = False, False, _msg, None
else:
    available, testable, why_not = True, False, None
    which = "jupyter_rfb"


# -------------------------------------------------------------- capability ---

capability = dict(
    title=False,
    size=True,
    position=False,
    show=False,
    vsync=False,
    resizable=True,
    decorate=False,
    fullscreen=False,
    context=False,  # Could work, but not implemented
    multi_window=True,
    scroll=True,
    parent=False,  # ipywidgets has layouts, but has no concept of parents
    always_on_top=False,
)


# ------------------------------------------------------- set_configuration ---

# The configuration mostly applies to the framebuffer. So if we'd want
# to implement some of that, we'd probably have to apply it to the FBO.


# ------------------------------------------------------------- application ---


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        super().__init__()

    def _vispy_get_backend_name(self):
        return 'jupyter_rfb'

    def _vispy_process_events(self):
        raise RuntimeError("Cannot process events while asyncio event-loop is running.")

    def _vispy_run(self):
        pass  # We're in IPython; don't enter a mainloop or we'll block!

    def _vispy_quit(self):
        pass

    def _vispy_get_native_app(self):
        return asyncio


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend, RemoteFrameBuffer):

    _double_click_supported = True

    def __init__(self, vispy_canvas, **kwargs):
        BaseCanvasBackend.__init__(self, vispy_canvas)
        RemoteFrameBuffer.__init__(self)
        # Use a context per canvas, because we seem to make assumptions
        # about OpenGL state being local to the canvas.
        self._context = OffscreenContext()  # OffscreenContext.get_global_instance()
        self._helper = FrameBufferHelper()
        self._loop = asyncio.get_event_loop()
        self._logical_size = 1, 1
        self._physical_size = 1, 1
        self._lifecycle = 0  # 0: not initialized, 1: initialized, 2: closed
        # Init more based on kwargs (could maybe handle, title, show, context)
        self._vispy_set_size(*kwargs["size"])
        self.resizable = kwargs["resizable"]
        # Need a first update
        self._vispy_update()

    def handle_event(self, ev):
        type = ev["event_type"]
        if type == "resize":
            # Note that jupyter_rfb already throttles this event
            w, h, r = ev["width"], ev["height"], ev["pixel_ratio"]
            self._logical_size = w, h
            self._physical_size = int(w * r), int(h * r)
            self._helper.set_physical_size(*self._physical_size)
            self._loop.call_soon(self._emit_resize_event)
            self._vispy_update()  # make sure to schedule a new draw
        elif type == "pointer_down":
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
            self._vispy_canvas.events.mouse_wheel(
                native=ev,
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
        elif type == "close":
            self._lifecycle = 2
            self._context.close()
            _stop_timers(self._vispy_canvas)
        else:
            pass  # event ignored / unknown

    def _modifiers(self, ev):
        return tuple(getattr(keys, m.upper()) for m in ev["modifiers"])

    def _emit_resize_event(self):
        self._vispy_canvas.events.resize(
            size=self._logical_size,
            physical_size=self._physical_size,
        )

    def get_frame(self):
        # This gets automatically called by the RFB widget

        # Only draw if the draw region is not null
        if self._physical_size[0] <= 1 or self._physical_size[1] <= 1:
            return None

        # Handle initialization
        if not self._lifecycle:
            self._lifecycle = 1
            self._vispy_canvas.set_current()
            self._vispy_canvas.events.initialize()
            self._emit_resize_event()

        # Draw and obtain result
        self._vispy_canvas.set_current()
        with self._helper:
            self._vispy_canvas.events.draw(region=None)
            array = self._helper.get_frame()

        # Flush commands here to clean up - otherwise we get errors related to
        # framebuffers not existin.
        self._vispy_canvas.context.flush_commands()

        return array

    def _vispy_warmup(self):
        self._vispy_canvas.set_current()

    def _vispy_set_current(self):
        self._context.make_current()

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
        if not visible:
            raise NotImplementedError("Cannot hide the RFB widget")

    def _vispy_set_fullscreen(self, fullscreen):
        raise NotImplementedError()

    def _vispy_update(self):
        self.request_draw()

    def _vispy_close(self):
        # ipywidget.Widget.close()  ->  closes the comm and removes all views
        self.close()

    def _vispy_get_size(self):
        return self._logical_size

    def _vispy_get_physical_size(self):
        return self._physical_size

    def _vispy_get_position(self):
        return 0, 0

    def _vispy_get_fullscreen(self):
        return False


# ------------------------------------------------------------------- timer ---

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
    # This is nice and all, but the Canvas object is frozen, so this is never actually used
    for attr in dir(canvas):
        try:
            attr_obj = getattr(canvas, attr)
        except NotImplementedError:
            continue  # prevent error due to props that we don't implement
        else:
            if isinstance(attr_obj, Timer):
                attr_obj.stop()
