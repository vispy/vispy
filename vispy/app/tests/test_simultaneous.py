# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_allclose
from nose.tools import assert_true

from vispy.app import Application, Canvas, Timer
from vispy.util.testing import (has_pyglet, has_qt, has_glfw, has_glut,  # noqa
                                requires_pyglet, requires_qt,
                                requires_glfw, requires_glut)  # noqa
from vispy.util.ptime import time
from vispy.gloo import gl
from vispy.gloo.util import _screenshot

_win_size = (200, 50)


def _update_process_check(canvas, val):
    """Update, process, and check result"""
    canvas.update()
    canvas.app.process_events()
    # check screenshot to see if it's all one color
    ss = _screenshot()
    assert_allclose(ss.shape[:2], _win_size[::-1])
    goal = val * np.ones(ss.shape)
    assert_allclose(ss, goal, atol=1)  # can be off by 1 due to rounding


def test_simultaneous_backends():
    """Test running multiple backends simultaneously"""
    checks = (has_qt, has_pyglet, has_glut, has_glfw)
    names = ('qt', 'pyglet', 'glut', 'glfw')
    backends = [name for name, check in zip(names, checks) if check()]
    canvases = dict()
    bgcolor = dict()
    for bi, backend in enumerate(backends):
        pos = [bi * 200, 0]
        canvas = Canvas(app=Application(backend), size=_win_size, position=pos,
                        title=backend + ' simul', show=True)
        canvas._warmup()
        canvases[backend] = canvas

        @canvas.events.paint.connect
        def paint(event):
            print('  {0:7}: {1}'.format(backend, bgcolor[backend]))
            gl.glClearColor(*bgcolor[backend])
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glFinish()

        bgcolor[backend] = [0.5, 0.5, 0.5, 1.0]
        gl.glViewport(0, 0, *list(_win_size))
        _update_process_check(canvases[backend], 127)

    for backend in backends:
        print('test %s' % backend)
        _update_process_check(canvases[backend], 127.5)
        bgcolor[backend] = [1., 1., 1., 1.]
        _update_process_check(canvases[backend], 255)
        bgcolor[backend] = [0.25, 0.25, 0.25, 0.25]
        _update_process_check(canvases[backend], 64)

    for backend in backends:
        canvases[backend].close()


def _test_same_app(backend):
    """Helper for testing multiple windows from the same application"""
    n_check = 3
    a = Application(backend)
    c0 = Canvas(app=a, size=_win_size, title=backend + ' same_0')
    c1 = Canvas(app=a, size=_win_size, title=backend + ' same_1')
    count = [0, 0]

    @c0.events.paint.connect
    def paint0(event):
        count[0] += 1
        c0.update()

    @c1.events.paint.connect  # noqa, analysis:ignore
    def paint1(event):
        count[1] += 1
        c1.update()

    c0.show()
    c1.show()
    timeout = time() + 2.0
    while (count[0] < n_check or count[1] < n_check) and time() < timeout:
        a.process_events()
    print((count, n_check))
    assert_true(n_check <= count[0] <= n_check + 1)
    assert_true(n_check <= count[1] <= n_check + 1)

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
    c0.close()
    c1.close()


def _test_multiple_app_same_backend(backend):
    """Helper to test using multiple windows for the same backend"""
    a = Application(backend)
    c0 = Canvas(app=a, size=_win_size, show=True, title=backend)
    c1 = Canvas(app=a, size=_win_size, show=True, title=backend)
    c0._warmup()
    c1._warmup()
    bgcolor = [0., 0., 0., 1.]

    @c0.events.paint.connect
    def paint0(event):
        print('  {0:7}_0: {1}'.format(backend, bgcolor))
        gl.glClearColor(*bgcolor)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glFinish()

    @c1.events.paint.connect
    def paint1(event):
        print('  {0:7}_1: {1}'.format(backend, bgcolor))
        gl.glClearColor(*bgcolor)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glFinish()

    for canvas in (c0, c1):
        bgcolor = [0.5, 0.5, 0.5, 1.0]
        gl.glViewport(0, 0, *list(_win_size))
        _update_process_check(canvas, 127)

    for canvas in (c0, c1):
        print('test %s' % backend)
        _update_process_check(canvas, 127.5)
        bgcolor = [1., 1., 1., 1.]
        _update_process_check(canvas, 255)
        bgcolor = [0.25, 0.25, 0.25, 0.25]
        _update_process_check(canvas, 64)

    c0.close()
    c1.close()


@requires_pyglet()
def test_pyglet():
    """Test multiple Pyglet windows"""
    _test_same_app('Pyglet')


@requires_glfw()
def test_glfw():
    """Test multiple Glfw windows"""
    _test_same_app('Glfw')


@requires_qt()
def test_qt():
    """Test multiple Qt windows"""
    _test_same_app('qt')


@requires_glut()
def test_glut():
    """Test multiple Glut windows"""
    _test_same_app('Glut')
