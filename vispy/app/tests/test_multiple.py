# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_array_equal

from vispy.app import Application, Canvas
from vispy.util.testing import (has_pyglet, has_qt, has_glfw, has_glut)  # noqa
from vispy.gloo import gl
from vispy.gloo.util import _screenshot


_win_size = (100, 50)


def _check_ss(val):
    # check screenshot to see if it's all one color
    ss = _screenshot()
    assert_array_equal(ss.shape[:2], _win_size[::-1])
    goal = np.ones_like(ss)
    goal.fill(val)
    assert_array_equal(ss, goal)


def _up_proc(a, c):
    c.update()
    a.process_events()
    c.swap_buffers()


def test_multiple_backends():
    """Test running multiple backends simultaneously"""
    checks = (has_qt, has_pyglet, has_glut)  # XXX GLFW is broken
    names = ('qt', 'pyglet', 'glut')
    backends = [name for name, check in zip(names, checks) if check()]
    apps = dict()
    canvases = dict()
    bgcolor = dict()
    for bi, backend in enumerate(backends):
        pos = [bi * 200, 0]
        apps[backend] = Application(backend)
        canvas = Canvas(app=apps[backend], size=_win_size, position=pos,
                        title=backend)
        canvases[backend] = canvas
        bgcolor[backend] = [0.5, 0.5, 0.5, 1.0]

        @canvas.events.resize.connect
        def resize(event):
            gl.glViewport(0, 0, *event.size)

        @canvas.events.paint.connect
        def paint(event):
            print('  {0:7}: {1}'.format(backend, bgcolor[backend]))
            gl.glClearColor(*bgcolor[backend])
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glFinish()

        canvas.show()
        t = 0.1 if backend == 'glut' else 0  # XXX Glut needs some time :(
        import time
        for _ in range(5):  # XXX all backends need a warmup???
            time.sleep(t)
            _up_proc(apps[backend], canvas)
        _check_ss(127)

    for backend in backends:
        print('test %s' % backend)
        _up_proc(apps[backend], canvases[backend])
        _check_ss(127)
        bgcolor[backend] = [1., 1., 1., 1.]
        _up_proc(apps[backend], canvases[backend])
        _check_ss(255)
        bgcolor[backend] = [0.25, 0.25, 0.25, 0.25]
        _up_proc(apps[backend], canvases[backend])
        _check_ss(64)
        canvases[backend].close()
