import os
from nose.tools import assert_equal, assert_raises

from vispy.util.testing import requires_application
from vispy.app import Canvas
from vispy.gloo import (get_gl_configuration, VertexShader, FragmentShader,
                        Program, check_error)


@requires_application()
def test_context_properties():
    """Test setting context properties"""
    # stereo, double buffer won't work on every sys
    contexts = (dict(samples=4), dict(stencil_size=8),
                dict(stencil_size=8, samples=4))
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
