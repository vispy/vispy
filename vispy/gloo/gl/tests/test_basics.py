"""Test to verify some basic functionality of our OpenGL API. We cover
much more in the test_functionality. Together, these two tests should
touch *all* ES 2.0 API calls.

The only exception is glCompressedTexImage2D and glCompressedTexSubImage2D.
"""

import sys

from vispy.app import Canvas
from numpy.testing import assert_almost_equal
from vispy.testing import (requires_application, requires_pyopengl, SkipTest,
                           run_tests_if_main, assert_equal, assert_true)
from vispy.util import use_log_level
from vispy.gloo import gl


def teardown_module():
    gl.use_gl()  # Reset to default


@requires_application()
def test_basics_desktop():
    """Test desktop GL backend for basic functionality."""
    _test_basics('gl2')
    with Canvas():
        _test_setting_parameters()
        _test_enabling_disabling()
        _test_setting_stuff()
        _test_object_creation_and_deletion()
        _test_fbo()
        try:
            gl.gl2._get_gl_func('foo', None, ())
        except RuntimeError as exp:
            exp = str(exp)
            assert 'version' in exp
            assert 'unknown' not in exp
        gl.glFinish()


@requires_application()
def test_functionality_proxy():
    """Test GL proxy class for basic functionality."""
    # By using debug mode, we are using the proxy class
    _test_basics('gl2 debug')


@requires_application()
@requires_pyopengl()
def test_basics_pypengl():
    """Test pyopengl GL backend for basic functionality."""
    _test_basics('pyopengl2')


@requires_application()
def test_functionality_es2():
    """Test es2 GL backend for basic functionality."""
    if True:
        raise SkipTest('Skip es2 functionality test for now.')
    if sys.platform.startswith('win'):
        raise SkipTest('Can only test es2 functionality on Windows.')
    _test_basics('es2')


def _test_basics(backend):
    """Create app and canvas so we have a context. Then run tests."""
    # use the backend
    with use_log_level('error', print_msg=False):
        gl.use_gl(backend)  # pyopengl throws warning on injection

    with Canvas():
        _test_setting_parameters()
        _test_enabling_disabling()
        _test_setting_stuff()
        _test_object_creation_and_deletion()
        _test_fbo()
        gl.glFinish()


def _test_setting_parameters():
    # Set some parameters and get result
    clr = 1.0, 0.1, 0.2, 0.7
    gl.glClearColor(*clr)
    assert_almost_equal(gl.glGetParameter(gl.GL_COLOR_CLEAR_VALUE), clr)
    #
    gl.glCullFace(gl.GL_FRONT)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_FRONT)
    gl.glCullFace(gl.GL_BACK)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_BACK)
    #
    gl.glDepthFunc(gl.GL_NOTEQUAL)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_FUNC), gl.GL_NOTEQUAL)
    #
    val = 0.2, 0.3
    gl.glDepthRange(*val)
    assert_almost_equal(gl.glGetParameter(gl.GL_DEPTH_RANGE), val)

    gl.check_error()


def _test_enabling_disabling():
    # Enabling/disabling
    gl.glEnable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), True)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 1)
    gl.glDisable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), False)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 0)
    #
    gl.glEnable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), True)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 1)
    gl.glDisable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), False)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 0)

    gl.check_error()


def _test_setting_stuff():
    # Set stuff to touch functions

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    #
    gl.glBlendColor(1.0, 1.0, 1.0, 1.0)
    gl.glBlendEquation(gl.GL_FUNC_ADD)
    gl.glBlendEquationSeparate(gl.GL_FUNC_ADD, gl.GL_FUNC_ADD)
    gl.glBlendFunc(gl.GL_ONE, gl.GL_ZERO)
    gl.glBlendFuncSeparate(gl.GL_ONE, gl.GL_ZERO, gl.GL_ONE, gl.GL_ZERO)
    #
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClearDepth(1)
    gl.glClearStencil(0)
    #
    gl.glColorMask(True, True, True, True)
    gl.glDepthMask(False)
    gl.glStencilMask(255)
    gl.glStencilMaskSeparate(gl.GL_FRONT, 128)
    #
    gl.glStencilFunc(gl.GL_ALWAYS, 0, 255)
    gl.glStencilFuncSeparate(gl.GL_FRONT, gl.GL_ALWAYS, 0, 255)
    gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)
    gl.glStencilOpSeparate(gl.GL_FRONT, gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)
    #
    gl.glFrontFace(gl.GL_CW)
    gl.glHint(gl.GL_GENERATE_MIPMAP_HINT, gl.GL_FASTEST)
    gl.glLineWidth(2.0)
    gl.glPolygonOffset(0.0, 0.0)
    gl.glSampleCoverage(1.0, False)

    # And getting stuff
    try:
        with use_log_level('error', print_msg=False):
            r, p = gl.glGetShaderPrecisionFormat(gl.GL_FRAGMENT_SHADER,
                                                 gl.GL_HIGH_FLOAT)
            gl.check_error()  # Sometimes the func is there but OpenGL errs
    except Exception:
        pass  # accept if the function is not there ...
        # We should catch RuntimeError and GL.error.NullFunctionError,
        # but PyOpenGL may not be available.
        # On Travis this function was not there on one machine according
        # to PyOpenGL, but our desktop backend worked fine ...

    #
    v = gl.glGetParameter(gl.GL_VERSION)
    assert_true(isinstance(v, str))
    assert_true(len(v) > 0)
    gl.check_error()


def _test_object_creation_and_deletion():

    # Stuff that is originally glGenX

    # Note that if we test glIsTexture(x), we cannot assume x to be a
    # nonexisting texture; we might have created a texture in another
    # test and failed to clean it up.

    # Create/delete texture
    # assert_equal(gl.glIsTexture(12), False)
    handle = gl.glCreateTexture()
    gl.glBindTexture(gl.GL_TEXTURE_2D, handle)
    assert_equal(gl.glIsTexture(handle), True)
    gl.glDeleteTexture(handle)
    assert_equal(gl.glIsTexture(handle), False)

    # Create/delete buffer
    # assert_equal(gl.glIsBuffer(12), False)
    handle = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, handle)
    assert_equal(gl.glIsBuffer(handle), True)
    gl.glDeleteBuffer(handle)
    assert_equal(gl.glIsBuffer(handle), False)

    # Create/delete framebuffer
    # assert_equal(gl.glIsFramebuffer(12), False)
    handle = gl.glCreateFramebuffer()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, handle)
    assert_equal(gl.glIsFramebuffer(handle), True)
    gl.glDeleteFramebuffer(handle)
    assert_equal(gl.glIsFramebuffer(handle), False)

    # Create/delete renderbuffer
    # assert_equal(gl.glIsRenderbuffer(12), False)
    handle = gl.glCreateRenderbuffer()
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, handle)
    assert_equal(gl.glIsRenderbuffer(handle), True)
    gl.glDeleteRenderbuffer(handle)
    assert_equal(gl.glIsRenderbuffer(handle), False)

    # Stuff that is originally called glCreate

    # Create/delete program
    # assert_equal(gl.glIsProgram(12), False)
    handle = gl.glCreateProgram()
    assert_equal(gl.glIsProgram(handle), True)
    gl.glDeleteProgram(handle)
    assert_equal(gl.glIsProgram(handle), False)

    # Create/delete shader
    # assert_equal(gl.glIsShader(12), False)
    handle = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    assert_equal(gl.glIsShader(handle), True)
    gl.glDeleteShader(handle)
    assert_equal(gl.glIsShader(handle), False)

    gl.check_error()


def _test_fbo():

    w, h = 120, 130

    # Create frame buffer
    hframebuf = gl.glCreateFramebuffer()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, hframebuf)

    # Create render buffer (for depth)
    hrenderbuf = gl.glCreateRenderbuffer()
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, hrenderbuf)
    gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT16, w, h)
    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,
                                 gl.GL_RENDERBUFFER, hrenderbuf)

    # Create texture (for color)
    htex = gl.glCreateTexture()
    gl.glBindTexture(gl.GL_TEXTURE_2D, htex)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, gl.GL_RGB,
                    gl.GL_UNSIGNED_BYTE, (h, w))
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                              gl.GL_TEXTURE_2D, htex, 0)

    # Check framebuffer status
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    assert_equal(status, gl.GL_FRAMEBUFFER_COMPLETE)

    # Tests renderbuffer params
    name = gl.glGetFramebufferAttachmentParameter(
        gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,
        gl.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME)
    assert_equal(name, hrenderbuf)
    #
    width = gl.glGetRenderbufferParameter(gl.GL_RENDERBUFFER,
                                          gl.GL_RENDERBUFFER_WIDTH)
    assert_equal(width, w)

    # Touch copy tex functions
    gl.glBindTexture(gl.GL_TEXTURE_2D, htex)
    gl.glCopyTexSubImage2D(gl.GL_TEXTURE_2D, 0, 5, 5, 5, 5, 20, 20)
    gl.glCopyTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, 0, 0, 30, 30, 0)

    gl.check_error()

    # Clean up
    gl.glDeleteTexture(htex)
    gl.glDeleteRenderbuffer(hrenderbuf)
    gl.glDeleteFramebuffer(hframebuf)

    gl.check_error()


run_tests_if_main()
