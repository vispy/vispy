import os
import sys

from vispy.testing import (requires_application, SkipTest, run_tests_if_main,
                           assert_equal, assert_raises)
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

    # stereo, double buffer won't work on every sys
    configs = [dict(samples=4), dict(stencil_size=8),
               dict(samples=4, stencil_size=8)]
    if a.backend_name.lower() != 'glfw':  # glfw *always* double-buffers
        configs.append(dict(double_buffer=False, samples=4))
        configs.append(dict(double_buffer=False))
    else:
        assert_raises(RuntimeError, Canvas, app=a,
                      config=dict(double_buffer=False))
    if a.backend_name.lower() == 'sdl2' and os.getenv('TRAVIS') == 'true':
        raise SkipTest('Travis SDL cannot set context')
    for config in configs:
        n_items = len(config)
        with Canvas(config=config):
            if 'true' in (os.getenv('TRAVIS', ''),
                          os.getenv('APPVEYOR', '').lower()):
                # Travis and Appveyor cannot handle obtaining these values
                props = config
            else:
                props = get_gl_configuration()
            assert_equal(len(config), n_items)
            for key, val in config.items():
                # XXX knownfail for windows samples, and wx (all platforms)
                if key == 'samples':
                    iswx = a.backend_name.lower() == 'wx'
                    if not (sys.platform.startswith('win') or iswx):
                        assert_equal(val, props[key], key)
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
