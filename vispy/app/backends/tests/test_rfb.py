# This currenly only tests that the backend exists and can be imported ...

import numpy as np
from vispy import gloo
from vispy.app import Application, Canvas
from vispy.app.backends import _jupyter_rfb
from vispy.testing import run_tests_if_main, requires_application
import pytest

try:
    import jupyter_rfb
except ImportError:
    jupyter_rfb = None


def test_rfb_app():

    # Raw
    app_backend = _jupyter_rfb.ApplicationBackend()

    # Test that run and quit don't do anything - Jupyter is an interactive session!
    app_backend._vispy_run()
    app_backend._vispy_quit()


class MyCanvas(Canvas):

    def on_draw(self, event):
        gloo.set_clear_color((0, 1, 0))
        gloo.clear()


@pytest.mark.skipif(jupyter_rfb is None, reason='jupyter_rfb is not installed')
@requires_application()
def test_rfb_canvas():

    app = Application("jupyter_rfb")
    canvas = MyCanvas(app=app)
    canvas_backend = canvas.native

    assert isinstance(canvas_backend, _jupyter_rfb.CanvasBackend)

    # Check that resize works
    assert "42" not in canvas_backend.css_width
    canvas.size = 42, 42
    assert canvas_backend.css_width == "42px"
    # Manually mimic what a browser would do, but round to 50
    canvas_backend.handle_event({"event_type": "resize", "width": 50, "height": 50, "pixel_ratio": 2.0})
    assert canvas.size == (50, 50)
    assert canvas.physical_size == (100, 100)

    # Mimic a draw
    frame = canvas_backend.get_frame()
    assert frame.shape[:2] == (100, 100)
    assert np.all(frame[:, :, 0] == 0)
    assert np.all(frame[:, :, 1] == 255)

    # Pretend that the user resized in the browser
    canvas_backend.handle_event({"event_type": "resize", "width": 60, "height": 60, "pixel_ratio": 1.0})
    assert canvas.size == (60, 60)
    assert canvas.physical_size == (60, 60)

    # Mimic another draw
    frame = canvas_backend.get_frame()
    assert frame.shape[:2] == (60, 60)
    assert np.all(frame[:, :, 0] == 0)
    assert np.all(frame[:, :, 1] == 255)

    # Test mouse event
    events = []
    canvas.events.mouse_press.connect(lambda e: events.append(e))
    canvas_backend.handle_event({"event_type": "pointer_down", "x": 11, "y": 12, "button": 1, "modifiers": []})
    assert len(events) == 1
    assert tuple(events[0].pos) == (11, 12)


run_tests_if_main()
