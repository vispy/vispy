# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_allclose

from vispy.app import Application, Canvas
from vispy.util.testing import (has_pyglet, has_qt, has_glfw, has_glut)  # noqa
from vispy.gloo import gl
from vispy.gloo.util import _screenshot

_win_size = (100, 50)


def _up_proc_check(canvas, val):
    """Update, process, and check result"""
    canvas.update()
    canvas.app.process_events()
    # check screenshot to see if it's all one color
    ss = _screenshot()
    assert_allclose(ss.shape[:2], _win_size[::-1])
    goal = val * np.ones(ss.shape)
    assert_allclose(ss, goal, atol=1)  # can be off by 1 due to rounding


def test_multiple_backends():
    """Test running multiple backends simultaneously"""
    checks = (has_qt, has_pyglet, has_glut, has_glfw)
    names = ('qt', 'pyglet', 'glut')  # , 'glfw') has issues XXX
    backends = [name for name, check in zip(names, checks) if check()]
    canvases = dict()
    bgcolor = dict()
    for bi, backend in enumerate(backends):
        pos = [bi * 200, 0]
        canvas = Canvas(app=Application(backend), size=_win_size, position=pos,
                        title=backend, show=True)
        canvas._warmup()
        canvases[backend] = canvas
        bgcolor[backend] = [0.5, 0.5, 0.5, 1.0]

        @canvas.events.paint.connect
        def paint(event):
            print('  {0:7}: {1}'.format(backend, bgcolor[backend]))
            gl.glClearColor(*bgcolor[backend])
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glFinish()

        gl.glViewport(0, 0, *list(_win_size))
        _up_proc_check(canvas, 127)

    for backend in backends:
        print('test %s' % backend)
        _up_proc_check(canvases[backend], 127.5)
        bgcolor[backend] = [1., 1., 1., 1.]
        _up_proc_check(canvases[backend], 255)
        bgcolor[backend] = [0.25, 0.25, 0.25, 0.25]
        _up_proc_check(canvases[backend], 64)
        canvases[backend].close()
