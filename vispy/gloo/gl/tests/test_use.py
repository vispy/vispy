""" Test the use function.
"""

from vispy.util import assert_is

from vispy.gloo import gl


def teardown_module():
    gl.use()  # Reset to default


@gl._requires_pyopengl()
def test_use_desktop():
    """ Testing that gl.use injects all names in gl namespace """

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
    
    # Touch debug wrapper stuff
    gl.use('desktop debug')
    
    # Use desktop again
    gl.use('desktop')
    #
    for name in dir(gl.desktop):
        if name.lower().startswith('gl'):
            val1 = getattr(gl, name)
            val2 = getattr(gl.desktop, name)
            assert_is(val1, val2)
