# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_array_equal

from vispy.app import Application, Canvas
from vispy.util.testing import (has_pyglet, has_qt, has_glfw,
                                has_glut, requires_application)
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
    a.process_events()
    c.update()
    a.process_events()


@requires_application()
def test_multiple_backends():
    """Test running multiple backends simultaneously"""
    checks = (has_qt, has_pyglet, has_glut, has_glfw)
    names = ('qt', 'pyglet', 'glut', 'glfw')
    backends = [name for name, check in zip(names, checks) if check()]
    apps = list()
    canvases = list()
    bgcolor = dict()
    print('init')
    for bi, backend in enumerate(backends):
        a = Application(backend)
        c = Canvas(app=a, size=_win_size, title=backend)
        bgcolor[backend] = [0, 0, 0, 1]

        @c.events.initialize.connect
        def initialize(event):
            gl.glViewport(0, 0, *c.size)  # does not work for GLUT or GLFW XXX

        @c.events.paint.connect
        def paint(event):
            print('  {0:7}: {1}'.format(backend, bgcolor[backend]))
            gl.glClearColor(*bgcolor[backend])
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glFinish()

        c.show()
        _up_proc(a, c)
        _check_ss(0)
        apps.append(a)
        canvases.append(c)

    print('test')
    for backend, a, c in zip(backends, apps, canvases):
        _up_proc(a, c)
        _check_ss(0)
        bgcolor[backend] = [1, 1, 1, 1]
        for _ in range(3):
            _up_proc(a, c)
            _check_ss(255)
        bgcolor[backend] = [0.5, 0.5, 0.5, 0.5]
        for _ in range(3):
            _up_proc(a, c)
            _check_ss(127)
        #c.close()  # XXX breaks GLFW b/c GLFW doesn't render to its own window

    #for c in canvases:  # XXX enabling breaks GLUT, possibly b/c of GLFW?
    #    c.close()

if __name__ == '__main__':
    test_multiple_backends()
