# -*- coding: utf-8 -*-

import numpy as np
import sys
from numpy.testing import assert_allclose
from nose.tools import assert_true
from time import sleep

from vispy.app import Application, Canvas, Timer
from vispy.app.backends import BACKEND_NAMES
from vispy.util.testing import has_backend, requires_application
from vispy.util.ptime import time
from vispy.gloo import gl
from vispy.gloo.util import _screenshot

_win_size = (200, 50)
_err_sleep_time = 0.
_ig_fail = True


def _update_process_check(canvas, val, paint=True, ignore_fail=False):
    """Update, process, and check result"""
    if paint:
        canvas.update()
        canvas.app.process_events()
        canvas.app.process_events()
    canvas._backend._vispy_set_current()
    print('           check %s' % val)
    # check screenshot to see if it's all one color
    ss = _screenshot()
    try:
        assert_allclose(ss.shape[:2], _win_size[::-1])
    except Exception:
        print('!!!!!!!!!! FAIL  bad size %s' % list(ss.shape[:2]))
        sleep(_err_sleep_time)
        if not ignore_fail:
            raise
    goal = val * np.ones(ss.shape)
    try:
        assert_allclose(ss, goal, atol=1)  # can be off by 1 due to rounding
    except Exception:
        print('!!!!!!!!!! FAIL  %s' % np.unique(ss))
        sleep(_err_sleep_time)
        if not ignore_fail:
            raise


def test_simultaneous_backends():
    """Test running multiple backends simultaneously"""
    # XXX knownfail Note: All the _update_process_check calls have
    # been crippled here because they don't work 100% of the time
    # depending on backend order, etc. This is not critical for
    # the software currently, so we let it slide for now.
    names = BACKEND_NAMES
    if sys.platform == 'darwin':
        names.pop(names.index('glut'))  # XXX knownfail, for unknown reason...
    backends = [name for name in names if has_backend(name)]
    canvases = dict()
    bgcolor = dict()
    try:
        for bi, backend in enumerate(backends):
            canvas = Canvas(app=backend, size=_win_size,
                            title=backend + ' simul', autoswap=False)
            canvas.__enter__()  # invoke warmup
            canvases[backend] = canvas

            @canvas.events.paint.connect
            def paint(event):
                print('  {0:7}: {1}'.format(backend, bgcolor[backend]))
                gl.glViewport(0, 0, *list(_win_size))
                gl.glClearColor(*bgcolor[backend])
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                gl.glFinish()

            bgcolor[backend] = [0.5, 0.5, 0.5, 1.0]
            _update_process_check(canvases[backend], 127)

        for backend in backends:
            print('test %s' % backend)
            _update_process_check(canvases[backend], 127, False, _ig_fail)
            bgcolor[backend] = [1., 1., 1., 1.]
            _update_process_check(canvases[backend], 255, True, _ig_fail)
            bgcolor[backend] = [0.25, 0.25, 0.25, 0.25]
            _update_process_check(canvases[backend], 64, True, _ig_fail)

        # now we do the same thing, but with sequential close() calls
        for backend in backends:
            print('test %s' % backend)
            _update_process_check(canvases[backend], 64, False, _ig_fail)
            bgcolor[backend] = [1., 1., 1., 1.]
            _update_process_check(canvases[backend], 255, True, _ig_fail)
            bgcolor[backend] = [0.25, 0.25, 0.25, 0.25]
            _update_process_check(canvases[backend], 64, True, _ig_fail)
    finally:
        for canvas in canvases.values():
            canvas.close()


def _test_multiple_canvases(backend):
    """Helper for testing multiple canvases from the same application"""
    n_check = 3
    a = Application(backend)
    with Canvas(app=a, size=_win_size, title=backend + ' same_0') as c0:
        with Canvas(app=a, size=_win_size, title=backend + ' same_1') as c1:
            ct = [0, 0]

            @c0.events.paint.connect
            def paint0(event):
                ct[0] += 1
                c0.update()

            @c1.events.paint.connect  # noqa, analysis:ignore
            def paint1(event):
                ct[1] += 1
                c1.update()

            c0.show()  # ensure visible
            c1.show()
            c0.update()  # force first paint
            c1.update()

            timeout = time() + 2.0
            while (ct[0] < n_check or ct[1] < n_check) and time() < timeout:
                a.process_events()
            print((ct, n_check))
            assert_true(n_check <= ct[0] <= n_check + 1)
            assert_true(n_check <= ct[1] <= n_check + 1)

            # check timer
            global timer_ran
            timer_ran = False

            def on_timer(_):
                global timer_ran
                timer_ran = True
            timeout = time() + 2.0
            Timer(0.1, app=a, connect=on_timer, iterations=1, start=True)
            while not timer_ran and time() < timeout:
                a.process_events()
            assert_true(timer_ran)


def _test_multiple_canvas_same_backend(backend):
    """Helper to test using multiple windows for the same backend"""
    a = Application(backend)
    kwargs = dict(app=a, autoswap=False, size=_win_size)
    with Canvas(title=backend + '_0', **kwargs) as c0:
        with Canvas(title=backend + '_1', **kwargs) as c1:
            for canvas, pos in zip((c0, c1), ((0, 0), (_win_size[0], 0))):
                canvas.show()
                canvas.position = pos
                canvas.app.process_events()
            bgcolors = [None] * 2

            @c0.events.paint.connect
            def paint0(event):
                print('  {0:7}: {1}'.format(backend + '_0', bgcolors[0]))
                if bgcolors[0] is not None:
                    gl.glViewport(0, 0, *list(_win_size))
                    gl.glClearColor(*bgcolors[0])
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                    gl.glFinish()

            @c1.events.paint.connect
            def paint1(event):
                print('  {0:7}: {1}'.format(backend + '_1', bgcolors[1]))
                if bgcolors[1] is not None:
                    gl.glViewport(0, 0, *list(_win_size))
                    gl.glClearColor(*bgcolors[1])
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                    gl.glFinish()

            for ci, canvas in enumerate((c0, c1)):
                print('paint %s' % canvas.title)
                bgcolors[ci] = [0.5, 0.5, 0.5, 1.0]
                _update_process_check(canvas, 127)

            for ci, canvas in enumerate((c0, c1)):
                print('test %s' % backend)
                _update_process_check(canvas, 127, paint=False)
                bgcolors[ci] = [1., 1., 1., 1.]
                _update_process_check(canvas, 255)
                bgcolors[ci] = [0.25, 0.25, 0.25, 0.25]
                _update_process_check(canvas, 64)


@requires_application('qt')
def test_qt():
    """Test multiple Qt windows"""
    _test_multiple_canvases('qt')
    if sys.platform != 'darwin':
        # OSX fails sometimes
        _test_multiple_canvas_same_backend('qt')  # XXX knownfail


@requires_application('pyglet')
def test_pyglet():
    """Test multiple Pyglet windows"""
    _test_multiple_canvases('pyglet')
    _test_multiple_canvas_same_backend('pyglet')


@requires_application('glfw')
def test_glfw():
    """Test multiple Glfw windows"""
    _test_multiple_canvases('glfw')
    _test_multiple_canvas_same_backend('glfw')


@requires_application('sdl2')
def test_sdl2():
    """Test multiple SDL2 windows"""
    _test_multiple_canvases('sdl2')
    _test_multiple_canvas_same_backend('sdl2')


@requires_application('glut')
def test_glut():
    """Test multiple Glut windows"""
    #_test_multiple_canvases('Glut')  # XXX knownfail, fails on OSX and Travis
    if sys.platform != 'darwin':
        _test_multiple_canvas_same_backend('glut')

if __name__ == '__main__':
    _ig_fail = False
    test_simultaneous_backends()
