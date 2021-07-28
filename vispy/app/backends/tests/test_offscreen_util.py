from vispy.app.backends._offscreen_util import OffscreenContext, FrameBufferHelper
from vispy.testing import run_tests_if_main, requires_application
from vispy import gloo
import numpy as np


@requires_application()
def test_offscreen_context():
    c1 = OffscreenContext()
    c2 = OffscreenContext.get_global_instance()
    c3 = OffscreenContext.get_global_instance()
    c4 = OffscreenContext()

    assert c1 is not c2
    assert c1 is not c4
    assert c2 is c3

    c1.make_current()
    c1.close()


class FakeCanvas(object):

    def __init__(self):
        self.context = gloo.GLContext()
        gloo.context.set_current_canvas(self)

    def flush(self):
        self.context.flush_commands()


@requires_application()
def test_frame_buffer_helper():
    canvas = FakeCanvas()
    gl_context = OffscreenContext()
    fbh = FrameBufferHelper()

    gl_context.make_current()
    fbh.set_physical_size(43, 67)
    with fbh:
        gloo.set_clear_color((0, 0.5, 1))
        gloo.clear()
        canvas.flush()
        array = fbh.get_frame()

    assert array.shape == (67, 43, 4)
    assert np.all(array[:, :, 0] == 0)
    assert np.all(array[:, :, 1] == 128)
    assert np.all(array[:, :, 2] == 255)


run_tests_if_main()
