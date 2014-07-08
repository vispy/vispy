""" Test the use function.
"""

from vispy.testing import assert_is, requires_pyopengl

from vispy.gloo import gl


def teardown_module():
    gl.use_gl()  # Reset to default


@requires_pyopengl()
def test_use_desktop():
    """ Testing that gl.use injects all names in gl namespace """

    # Use desktop
    gl.use_gl('desktop')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.desktop, name)
            assert_is(val1, val2)

    # Use pyopengl
    gl.use_gl('pyopengl')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.pyopengl, name)
            assert_is(val1, val2)
    
    # Use webgl
    gl.use_gl('webgl')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.webgl, name)
            assert_is(val1, val2)
    
    # Touch debug wrapper stuff
    gl.use_gl('desktop debug')
    
    # Use desktop again
    gl.use_gl('desktop')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.desktop, name)
            assert_is(val1, val2)


if __name__ == '__main__':
    test_use_desktop()
