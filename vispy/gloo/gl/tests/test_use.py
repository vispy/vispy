from nose.tools import assert_is

from vispy.gloo import gl

def test_use_desktop():
    """ Using that gl.use injects all names in gl namespace """
    
    # Use desktop
    gl.use('desktop')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.desktop, name)
            assert_is(val1, val2)
    
    # Use pyopengl
    gl.use('pyopengl')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.pyopengl, name)
            assert_is(val1, val2)
    
    # Use desktop again
    gl.use('desktop')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.desktop, name)
            assert_is(val1, val2)


if __name__ == '__main__':
    test_use_desktop()
