import sys

import pytest

from vispy.testing import (requires_application, SkipTest, run_tests_if_main,
                           assert_raises, IS_CI)
from vispy.app import Canvas, use_app
from vispy.gloo import get_gl_configuration, Program
from vispy.gloo.gl import check_error


@requires_application()
def test_context_properties():
    """Test setting context properties"""
    a = use_app()
    if a.backend_name.lower() == 'pyglet':
        return  # cannot set more than once on Pyglet
    if a.backend_name.lower() == 'osmesa':
        return  # cannot set config on OSMesa
    if 'pyqt5' in a.backend_name.lower() or 'pyqt6' in a.backend_name.lower() or 'pyside2' in a.backend_name.lower() or 'pyside6' in a.backend_name.lower():
        pytest.xfail("Context sharing is not supported in PyQt5, PyQt6, PySide2, or PySide6 at this time.")

    # stereo, double buffer won't work on every sys
    configs = [dict(samples=4), dict(stencil_size=8),
               dict(samples=4, stencil_size=8)]
    if a.backend_name.lower() != 'glfw':  # glfw *always* double-buffers
        configs.append(dict(double_buffer=False, samples=4))
        configs.append(dict(double_buffer=False))
    else:
        assert_raises(RuntimeError, Canvas, app=a,
                      config=dict(double_buffer=False))
    if a.backend_name.lower() == 'sdl2' and IS_CI:
        raise SkipTest('Travis SDL cannot set context')
    for config in configs:
        n_items = len(config)
        with Canvas(config=config):
            if IS_CI:
                # Travis and Appveyor cannot handle obtaining these values
                props = config
            else:
                props = get_gl_configuration()
            assert len(config) == n_items
            for key, val in config.items():
                # XXX knownfail for windows samples, and wx/tkinter (all platforms)
                if key == 'samples':
                    will_fail_backend = a.backend_name.lower() in ('wx', 'tkinter')
                    if not (sys.platform.startswith('win') or will_fail_backend):
                        assert val == props[key], key
    assert_raises(TypeError, Canvas, config='foo')
    assert_raises(KeyError, Canvas, config=dict(foo=True))
    assert_raises(TypeError, Canvas, config=dict(double_buffer='foo'))


@requires_application()
def test_context_sharing():
    """Test context sharing"""
    with Canvas() as c1:
        vert = "attribute vec4 pos;\nvoid main (void) {gl_Position = pos;}"
        frag = "void main (void) {gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);}"
        program = Program(vert, frag)
        program['pos'] = [(1, 2, 3, 1), (4, 5, 6, 1)]
        program.draw('points')

        def check():
            # Do something to program and see if it worked
            program['pos'] = [(1, 2, 3, 1), (4, 5, 6, 1)]  # Do command
            program.draw('points')
            check_error()

        # Check while c1 is active
        check()

        # pyqt5 does not currently support context sharing, pyside6 seg faults on app tests
        if 'pyqt5' in c1.app.backend_name.lower() or 'pyqt6' in c1.app.backend_name.lower() or 'pyside2' in c1.app.backend_name.lower() or 'pyside6' in c1.app.backend_name.lower():
            pytest.xfail("Context sharing is not supported in PyQt5, PyQt6, PySide2, or PySide6 at this time.")

        # Tkinter does not currently support context sharing
        if 'tk' in c1.app.backend_name.lower():
            pytest.xfail("Context sharing is not supported in Tkinter at this time.")

        # Check while c2 is active (with different context)
        with Canvas() as c2:
            # pyglet always shares
            if 'pyglet' not in c2.app.backend_name.lower():
                assert_raises(Exception, check)

        # Check while c2 is active (with *same* context)
        with Canvas(shared=c1.context) as c2:
            assert c1.context.shared is c2.context.shared  # same object
            check()

run_tests_if_main()
