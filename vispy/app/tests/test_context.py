import os
from nose.tools import assert_equal, assert_raises

from vispy.util.testing import requires_application, has_backend
from vispy.app import Canvas
from vispy.app.backends import BACKEND_NAMES
from vispy.gloo import (get_gl_configuration, VertexShader, FragmentShader,
                        Program, check_error)


@requires_application()
def test_context_properties():
    """Test setting context properties"""
    contexts = (dict(double_buffer=False),  # stereo won't work on every sys
                dict(samples=4), dict(stencil_size=8),
                dict(double_buffer=False, samples=4))
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


def test_context_sharing():
    """Test context sharing"""
    can = list()
    cannot = list()
    for backend in BACKEND_NAMES:
        if has_backend(backend):
            if has_backend(backend, capable=['context']):
                can.append(backend)
            else:
                cannot.append(backend)
    for backend in can:
        with Canvas(app=backend) as c1:
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

            with Canvas(app=backend):
                if backend.lower() != 'pyglet':  # pyglet always shares
                    assert_raises(RuntimeError, check)
            with Canvas(app=backend, context=c1.context):
                check()
    for backend in cannot:
        with Canvas(app=backend) as c1:
            assert_raises(RuntimeError, Canvas, app=backend,
                          context=c1.context)
