""" Test the use function.
"""

from vispy.testing import assert_is, requires_pyopengl

from vispy.gloo import gl
from vispy.testing import run_tests_if_main


def teardown_module():
    gl.use_gl()  # Reset to default


@requires_pyopengl()
def test_use_desktop():
    """ Testing that gl.use injects all names in gl namespace """

    # Use desktop
    gl.use_gl('gl2')
    #
    for name in dir(gl.gl2):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.gl2, name)
            assert_is(val1, val2)

    # Use pyopengl
    gl.use_gl('pyopengl2')
    #
    for name in dir(gl.gl2):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.pyopengl2, name)
            assert_is(val1, val2)
    
    # Use gl+ 
    gl.use_gl('gl+')
    # uses all ES2 names from pyopengl2 backend
    for name in dir(gl.gl2):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.pyopengl2, name)
            assert_is(val1, val2)
    # But provides extra names too
    for name in dir(gl.glplus):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.glplus, name)
            assert_is(val1, val2)
    
    # Use dummy
    gl.use_gl('dummy')
    #
    for name in dir(gl.gl2):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.dummy, name)
            assert_is(val1, val2)
    
    # Touch debug wrapper stuff
    gl.use_gl('gl2 debug')
    
    # Use desktop again
    gl.use_gl('gl2')
    #
    for name in dir(gl.gl2):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.gl2, name)
            assert_is(val1, val2)


run_tests_if_main()
