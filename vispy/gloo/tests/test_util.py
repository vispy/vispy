# -*- coding: utf-8 -*-

from vispy.gloo import util

from vispy.testing import run_tests_if_main, assert_raises


def test_check_enum():
    from vispy.gloo import gl

    # Test enums
    assert util.check_enum(gl.GL_RGB) == 'rgb' 
    assert util.check_enum(gl.GL_TRIANGLE_STRIP) == 'triangle_strip' 

    # Test strings
    assert util.check_enum('RGB') == 'rgb' 
    assert util.check_enum('Triangle_STRIp') == 'triangle_strip' 

    # Test wrong input
    assert_raises(ValueError, util.check_enum, int(gl.GL_RGB))
    assert_raises(ValueError, util.check_enum, int(gl.GL_TRIANGLE_STRIP))
    assert_raises(ValueError, util.check_enum, [])

    # Test with test
    util.check_enum('RGB', 'test', ('rgb', 'alpha')) == 'rgb' 
    util.check_enum(gl.GL_ALPHA, 'test', ('rgb', 'alpha')) == 'alpha' 
    #
    assert_raises(ValueError, util.check_enum, 'RGB', 'test', ('a', 'b'))
    assert_raises(ValueError, util.check_enum, gl.GL_ALPHA, 'test', ('a', 'b'))

    # Test PyOpenGL enums
    try:
        from OpenGL import GL
    except ImportError:
        return  # we cannot test PyOpenGL
    #
    assert util.check_enum(GL.GL_RGB) == 'rgb' 
    assert util.check_enum(GL.GL_TRIANGLE_STRIP) == 'triangle_strip' 


def test_check_identifier():

    # Tests check_identifier()
    assert util.check_identifier('foo') is None
    assert util.check_identifier('_fooBarBla') is None
    assert util.check_identifier('_glPosition') is None

    # Wrong identifier
    assert util.check_identifier('__').startswith('Identifier')
    assert util.check_identifier('gl_').startswith('Identifier')
    assert util.check_identifier('GL_').startswith('Identifier')
    assert util.check_identifier('double').startswith('Identifier')

    # Test check_variable()
    assert util.check_variable('foo') is None
    assert util.check_variable('a' * 30) is None
    assert util.check_variable('a' * 32)


run_tests_if_main()
