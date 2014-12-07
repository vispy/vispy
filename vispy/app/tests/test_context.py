import os
import sys
from nose.tools import assert_equal, assert_raises

from vispy.testing import requires_application, SkipTest, run_tests_if_main
from vispy.app import Canvas, use_app
from vispy.gloo import get_gl_configuration, Program
from vispy.gloo.gl import check_error


@requires_application()
def test_context_properties():
    """Test setting context properties"""
    a = use_app()
    if a.backend_name.lower() == 'pyglet':
        return  # cannot set more than once on Pyglet
    # stereo, double buffer won't work on every sys
    contexts = [dict(samples=4), dict(stencil_size=8),
                dict(samples=4, stencil_size=8)]
    if a.backend_name.lower() != 'glfw':  # glfw *always* double-buffers
        contexts.append(dict(double_buffer=False, samples=4))
        contexts.append(dict(double_buffer=False))
    else:
        assert_raises(RuntimeError, Canvas, app=a,
                      context=dict(double_buffer=False))
    if a.backend_name.lower() == 'sdl2' and os.getenv('TRAVIS') == 'true':
        raise SkipTest('Travis SDL cannot set context')
    for context in contexts:
        n_items = len(context)
        with Canvas(context=context):
            if 'true' in (os.getenv('TRAVIS', ''),
                          os.getenv('APPVEYOR', '').lower()):
                # Travis and Appveyor cannot handle obtaining these values
                props = context
            else:
                props = get_gl_configuration()
            assert_equal(len(context), n_items)
            for key, val in context.items():
                # XXX knownfail for windows samples, and wx (all platforms)
                if key == 'samples':
                    iswx = a.backend_name.lower() == 'wx'
                    if not (sys.platform.startswith('win') or iswx):
                        assert_equal(val, props[key], key)
    assert_raises(TypeError, Canvas, context='foo')
    assert_raises(KeyError, Canvas, context=dict(foo=True))
    assert_raises(TypeError, Canvas, context=dict(double_buffer='foo'))


@requires_application()
def test_context_sharing():
    """Test context sharing"""
    with Canvas() as c1:
        vert = "uniform vec4 pos;\nvoid main (void) {gl_Position = pos;}"
        frag = "uniform vec4 pos;\nvoid main (void) {gl_FragColor = pos;}"
        program = Program(vert, frag)
        program['pos'] = [1, 2, 3, 4]
        program._glir.flush()

        def check():
            # Do something to program and see if it worked
            program['pos'] = [1, 2, 3, 4]  # Do command
            program._glir.flush()  # Execute that command
            check_error()
        
        # Check while c1 is active
        check()
        
        # Check while c2 is active (with different context)
        with Canvas() as c2:
            # pyglet always shares
            if 'pyglet' not in c2.app.backend_name.lower():
                assert_raises(RuntimeError, check)
        
        # Tests unable to create canvas on glut
        if c1.app.backend_name.lower() in ('glut',):
            assert_raises(RuntimeError, Canvas, context=c1.context)
            return
        
        # Check while c2 is active (with *same* context)
        with Canvas(context=c1.context) as c2:
            assert c1.context is c2.context  # Same context object
            check()


run_tests_if_main()
