from nose.tools import assert_equal, assert_raises

from vispy.util.testing import requires_application, has_backend
from vispy.app import Canvas
from vispy.app.backends import BACKEND_NAMES
from vispy.gloo import get_gl_configuration


@requires_application()
def test_context_properties():
    """Test setting context properties"""
    contexts = (dict(stereo=True), dict(double_buffer=False),
                dict(samples=4), dict(stencil_size=8),
                dict(stereo=True, double_buffer=False, samples=4))
    for context in contexts:
        n_items = len(context)
        with Canvas(context=context):
            props = get_gl_configuration()
            assert_equal(len(context), n_items)
            for key, val in context.items():
                assert_equal(val, props[key])
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
            with Canvas(app=backend, context=c1.context) as c2:
                # XXX this should be better tested -- changing one thing
                # in one canvas should show up in the other
                print(c2)
    for backend in cannot:
        with Canvas(app=backend) as c1:
            assert_raises(RuntimeError, Canvas, app=backend,
                          context=c1.context)
