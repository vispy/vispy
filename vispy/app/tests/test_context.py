import os
import sys
from nose.tools import assert_equal, assert_raises

from vispy.testing import requires_application, SkipTest
from vispy.app import Canvas, use_app
from vispy.gloo import (get_gl_configuration, VertexShader, FragmentShader,
                        Program, check_error)


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
            if os.getenv('TRAVIS', 'false') == 'true':
                # Travis cannot handle obtaining these values
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
        vert = VertexShader("uniform vec4 pos;"
                            "void main (void) {gl_Position = pos;}")
        frag = FragmentShader("uniform vec4 pos;"
                              "void main (void) {gl_FragColor = pos;}")
        program = Program(vert, frag)
        program['pos'] = [1, 2, 3, 4]
        program.activate()  # should print

        def check():
            program.activate()
            check_error()

        with Canvas() as c:
            # pyglet always shares
            if 'pyglet' not in c.app.backend_name.lower():
                assert_raises(RuntimeError, check)
        if c1.app.backend_name.lower() in ('glut',):
            assert_raises(RuntimeError, Canvas, context=c1.context)
        else:
            with Canvas(context=c1.context):
                check()
