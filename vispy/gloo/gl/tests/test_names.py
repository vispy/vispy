"""Tests to verify that all ES 2.0 function names are defined in all
backends, and no more than that.
"""

from vispy.testing import requires_pyopengl

from vispy.gloo import gl
from vispy.testing import run_tests_if_main


def teardown_module():
    gl.use_gl()  # Reset to default


class _DummyObject:
    """To be able to import es2 even in Linux, so that we can test the
    names defined inside.
    """

    def LoadLibrary(self, fname):
        return _DummyObject()

    def __getattr__(self, name):
        setattr(self, name, self.__class__())
        return getattr(self, name)


def _test_function_names(mod):
    # The .difference(['gl2']) is to allow the gl2 module name
    fnames = set([name for name in dir(mod) if name.startswith('gl')])
    assert function_names.difference(fnames) == set()
    assert fnames.difference(function_names).difference(ok_names) == set()


def _test_constant_names(mod):
    cnames = set([name for name in dir(mod) if name.startswith('GL')])
    assert constant_names.difference(cnames) == set()
    assert cnames.difference(constant_names) == set()


def test_destop():
    """Desktop backend should have all ES 2.0 names. No more, no less."""
    from vispy.gloo.gl import gl2
    _test_function_names(gl2)
    _test_constant_names(gl2)


def test_es2():
    """es2 backend should have all ES 2.0 names. No more, no less."""
    # Import. Install a dummy lib so that at least we can import es2.
    try:
        from vispy.gloo.gl import es2  # noqa
    except Exception:
        import ctypes
        ctypes.TEST_DLL = _DummyObject()
    from vispy.gloo.gl import es2  # noqa

    # Test
    _test_function_names(es2)
    _test_constant_names(es2)


@requires_pyopengl()
def test_pyopengl():
    """Pyopengl backend should have all ES 2.0 names. No more, no less."""
    from vispy.gloo.gl import pyopengl2
    _test_function_names(pyopengl2)
    _test_constant_names(pyopengl2)


@requires_pyopengl()
def test_glplus():
    """Run glplus, check that mo names, set back, check exact set of names."""
    gl.use_gl('gl+')
    # Check that there are more names
    fnames = set([name for name in dir(gl) if name.startswith('gl')])
    assert len(fnames.difference(function_names).difference(['gl2'])) > 50
    cnames = set([name for name in dir(gl) if name.startswith('GL')])
    assert len(cnames.difference(constant_names)) > 50
    gl.use_gl('gl2')
    _test_function_names(gl)
    _test_constant_names(gl)


def test_proxy():
    """Glproxy class should have all ES 2.0 names. No more, no less."""
    _test_function_names(gl.proxy)
    _test_constant_names(gl._constants)


def test_main():
    """Main gl namespace should have all ES 2.0 names. No more, no less."""
    _test_function_names(gl)
    _test_constant_names(gl)


def _main():
    """For testing this test suite :)"""
    test_main()
    test_proxy()
    test_destop()
    test_es2()
    test_pyopengl()


# Note: I took these names below from _main and _constants, which is a
# possible cause for error.

function_names = """
glActiveTexture glAttachShader glBindAttribLocation glBindBuffer
glBindFramebuffer glBindRenderbuffer glBindTexture glBlendColor
glBlendEquation glBlendEquationSeparate glBlendFunc glBlendFuncSeparate
glBufferData glBufferSubData glCheckFramebufferStatus glClear
glClearColor glClearDepth glClearStencil glColorMask glCompileShader
glCompressedTexImage2D glCompressedTexSubImage2D glCopyTexImage2D
glCopyTexSubImage2D glCreateBuffer glCreateFramebuffer glCreateProgram
glCreateRenderbuffer glCreateShader glCreateTexture glCullFace
glDeleteBuffer glDeleteFramebuffer glDeleteProgram glDeleteRenderbuffer
glDeleteShader glDeleteTexture glDepthFunc glDepthMask glDepthRange
glDetachShader glDisable glDisableVertexAttribArray glDrawArrays
glDrawElements glEnable glEnableVertexAttribArray glFinish glFlush
glFramebufferRenderbuffer glFramebufferTexture2D glFrontFace
glGenerateMipmap glGetActiveAttrib glGetActiveUniform
glGetAttachedShaders glGetAttribLocation glGetBufferParameter glGetError
glGetFramebufferAttachmentParameter glGetParameter glGetProgramInfoLog
glGetProgramParameter glGetRenderbufferParameter glGetShaderInfoLog
glGetShaderParameter glGetShaderPrecisionFormat glGetShaderSource
glGetTexParameter glGetUniform glGetUniformLocation glGetVertexAttrib
glGetVertexAttribOffset glHint glIsBuffer glIsEnabled glIsFramebuffer
glIsProgram glIsRenderbuffer glIsShader glIsTexture glLineWidth
glLinkProgram glPixelStorei glPolygonOffset glReadPixels
glRenderbufferStorage glSampleCoverage glScissor glShaderSource
glStencilFunc glStencilFuncSeparate glStencilMask
glStencilMaskSeparate glStencilOp glStencilOpSeparate glTexImage2D
glTexParameterf glTexParameteri glTexSubImage2D glUniform1f glUniform1fv
glUniform1i glUniform1iv glUniform2f glUniform2fv glUniform2i
glUniform2iv glUniform3f glUniform3fv glUniform3i glUniform3iv
glUniform4f glUniform4fv glUniform4i glUniform4iv glUniformMatrix2fv
glUniformMatrix3fv glUniformMatrix4fv glUseProgram glValidateProgram
glVertexAttrib1f glVertexAttrib2f glVertexAttrib3f glVertexAttrib4f
glVertexAttribPointer glViewport
""".replace('\n', ' ')

constant_names = """
GL_ACTIVE_ATTRIBUTES GL_ACTIVE_ATTRIBUTE_MAX_LENGTH GL_ACTIVE_TEXTURE
GL_ACTIVE_UNIFORMS GL_ACTIVE_UNIFORM_MAX_LENGTH
GL_ALIASED_LINE_WIDTH_RANGE GL_ALIASED_POINT_SIZE_RANGE GL_ALPHA
GL_ALPHA_BITS GL_ALWAYS GL_ARRAY_BUFFER GL_ARRAY_BUFFER_BINDING
GL_ATTACHED_SHADERS GL_BACK GL_BLEND GL_BLEND_COLOR GL_BLEND_DST_ALPHA
GL_BLEND_DST_RGB GL_BLEND_EQUATION GL_BLEND_EQUATION_ALPHA
GL_BLEND_EQUATION_RGB GL_BLEND_SRC_ALPHA GL_BLEND_SRC_RGB GL_BLUE_BITS
GL_BOOL GL_BOOL_VEC2 GL_BOOL_VEC3 GL_BOOL_VEC4 GL_BUFFER_SIZE
GL_BUFFER_USAGE GL_BYTE GL_CCW GL_CLAMP_TO_EDGE GL_COLOR_ATTACHMENT0
GL_COLOR_BUFFER_BIT GL_COLOR_CLEAR_VALUE GL_COLOR_WRITEMASK
GL_COMPILE_STATUS GL_COMPRESSED_TEXTURE_FORMATS GL_CONSTANT_ALPHA
GL_CONSTANT_COLOR GL_CULL_FACE GL_CULL_FACE_MODE GL_CURRENT_PROGRAM
GL_CURRENT_VERTEX_ATTRIB GL_CW GL_DECR GL_DECR_WRAP GL_DELETE_STATUS
GL_DEPTH_ATTACHMENT GL_DEPTH_BITS GL_DEPTH_BUFFER_BIT
GL_DEPTH_CLEAR_VALUE GL_DEPTH_COMPONENT GL_DEPTH_COMPONENT16
GL_DEPTH_FUNC GL_DEPTH_RANGE GL_DEPTH_TEST GL_DEPTH_WRITEMASK GL_DITHER
GL_DONT_CARE GL_DST_ALPHA GL_DST_COLOR GL_DYNAMIC_DRAW
GL_ELEMENT_ARRAY_BUFFER GL_ELEMENT_ARRAY_BUFFER_BINDING GL_EQUAL
GL_ES_VERSION_2_0 GL_EXTENSIONS GL_FALSE GL_FASTEST GL_FIXED GL_FLOAT
GL_FLOAT_MAT2 GL_FLOAT_MAT3 GL_FLOAT_MAT4 GL_FLOAT_VEC2 GL_FLOAT_VEC3
GL_FLOAT_VEC4 GL_FRAGMENT_SHADER GL_FRAMEBUFFER
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL GL_FRAMEBUFFER_BINDING
GL_FRAMEBUFFER_COMPLETE GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT
GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS
GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT GL_FRAMEBUFFER_UNSUPPORTED
GL_FRONT GL_FRONT_AND_BACK GL_FRONT_FACE GL_FUNC_ADD
GL_FUNC_REVERSE_SUBTRACT GL_FUNC_SUBTRACT GL_GENERATE_MIPMAP_HINT
GL_GEQUAL GL_GREATER GL_GREEN_BITS GL_HIGH_FLOAT GL_HIGH_INT
GL_IMPLEMENTATION_COLOR_READ_FORMAT GL_IMPLEMENTATION_COLOR_READ_TYPE
GL_INCR GL_INCR_WRAP GL_INFO_LOG_LENGTH GL_INT GL_INT_VEC2 GL_INT_VEC3
GL_INT_VEC4 GL_INVALID_ENUM GL_INVALID_FRAMEBUFFER_OPERATION
GL_INVALID_OPERATION GL_INVALID_VALUE GL_INVERT GL_KEEP GL_LEQUAL
GL_LESS GL_LINEAR GL_LINEAR_MIPMAP_LINEAR GL_LINEAR_MIPMAP_NEAREST
GL_LINES GL_LINE_LOOP GL_LINE_STRIP GL_LINE_WIDTH GL_LINK_STATUS
GL_LOW_FLOAT GL_LOW_INT GL_LUMINANCE GL_LUMINANCE_ALPHA
GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS GL_MAX_CUBE_MAP_TEXTURE_SIZE
GL_MAX_FRAGMENT_UNIFORM_VECTORS GL_MAX_RENDERBUFFER_SIZE
GL_MAX_TEXTURE_IMAGE_UNITS GL_MAX_TEXTURE_SIZE GL_MAX_VARYING_VECTORS
GL_MAX_VERTEX_ATTRIBS GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS
GL_MAX_VERTEX_UNIFORM_VECTORS GL_MAX_VIEWPORT_DIMS GL_MEDIUM_FLOAT
GL_MEDIUM_INT GL_MIRRORED_REPEAT GL_NEAREST GL_NEAREST_MIPMAP_LINEAR
GL_NEAREST_MIPMAP_NEAREST GL_NEVER GL_NICEST GL_NONE GL_NOTEQUAL
GL_NO_ERROR GL_NUM_COMPRESSED_TEXTURE_FORMATS
GL_NUM_SHADER_BINARY_FORMATS GL_ONE GL_ONE_MINUS_CONSTANT_ALPHA
GL_ONE_MINUS_CONSTANT_COLOR GL_ONE_MINUS_DST_ALPHA
GL_ONE_MINUS_DST_COLOR GL_ONE_MINUS_SRC_ALPHA GL_ONE_MINUS_SRC_COLOR
GL_OUT_OF_MEMORY GL_PACK_ALIGNMENT GL_POINTS GL_POLYGON_OFFSET_FACTOR
GL_POLYGON_OFFSET_FILL GL_POLYGON_OFFSET_UNITS GL_RED_BITS
GL_RENDERBUFFER GL_RENDERBUFFER_ALPHA_SIZE GL_RENDERBUFFER_BINDING
GL_RENDERBUFFER_BLUE_SIZE GL_RENDERBUFFER_DEPTH_SIZE
GL_RENDERBUFFER_GREEN_SIZE GL_RENDERBUFFER_HEIGHT
GL_RENDERBUFFER_INTERNAL_FORMAT GL_RENDERBUFFER_RED_SIZE
GL_RENDERBUFFER_STENCIL_SIZE GL_RENDERBUFFER_WIDTH GL_RENDERER GL_REPEAT
GL_REPLACE GL_RGB GL_RGB565 GL_RGB5_A1 GL_RGBA GL_RGBA4 GL_SAMPLER_2D
GL_SAMPLER_CUBE GL_SAMPLES GL_SAMPLE_ALPHA_TO_COVERAGE GL_SAMPLE_BUFFERS
GL_SAMPLE_COVERAGE GL_SAMPLE_COVERAGE_INVERT GL_SAMPLE_COVERAGE_VALUE
GL_SCISSOR_BOX GL_SCISSOR_TEST GL_SHADER_BINARY_FORMATS
GL_SHADER_COMPILER GL_SHADER_SOURCE_LENGTH GL_SHADER_TYPE
GL_SHADING_LANGUAGE_VERSION GL_SHORT GL_SRC_ALPHA GL_SRC_ALPHA_SATURATE
GL_SRC_COLOR GL_STATIC_DRAW GL_STENCIL_ATTACHMENT GL_STENCIL_BACK_FAIL
GL_STENCIL_BACK_FUNC GL_STENCIL_BACK_PASS_DEPTH_FAIL
GL_STENCIL_BACK_PASS_DEPTH_PASS GL_STENCIL_BACK_REF
GL_STENCIL_BACK_VALUE_MASK GL_STENCIL_BACK_WRITEMASK GL_STENCIL_BITS
GL_STENCIL_BUFFER_BIT GL_STENCIL_CLEAR_VALUE GL_STENCIL_FAIL
GL_STENCIL_FUNC GL_STENCIL_INDEX8 GL_STENCIL_PASS_DEPTH_FAIL
GL_STENCIL_PASS_DEPTH_PASS GL_STENCIL_REF GL_STENCIL_TEST
GL_STENCIL_VALUE_MASK GL_STENCIL_WRITEMASK GL_STREAM_DRAW
GL_SUBPIXEL_BITS GL_TEXTURE GL_TEXTURE0 GL_TEXTURE1 GL_TEXTURE10
GL_TEXTURE11 GL_TEXTURE12 GL_TEXTURE13 GL_TEXTURE14 GL_TEXTURE15
GL_TEXTURE16 GL_TEXTURE17 GL_TEXTURE18 GL_TEXTURE19 GL_TEXTURE2
GL_TEXTURE20 GL_TEXTURE21 GL_TEXTURE22 GL_TEXTURE23 GL_TEXTURE24
GL_TEXTURE25 GL_TEXTURE26 GL_TEXTURE27 GL_TEXTURE28 GL_TEXTURE29
GL_TEXTURE3 GL_TEXTURE30 GL_TEXTURE31 GL_TEXTURE4 GL_TEXTURE5
GL_TEXTURE6 GL_TEXTURE7 GL_TEXTURE8 GL_TEXTURE9 GL_TEXTURE_2D
GL_TEXTURE_BINDING_2D GL_TEXTURE_BINDING_CUBE_MAP GL_TEXTURE_CUBE_MAP
GL_TEXTURE_CUBE_MAP_NEGATIVE_X GL_TEXTURE_CUBE_MAP_NEGATIVE_Y
GL_TEXTURE_CUBE_MAP_NEGATIVE_Z GL_TEXTURE_CUBE_MAP_POSITIVE_X
GL_TEXTURE_CUBE_MAP_POSITIVE_Y GL_TEXTURE_CUBE_MAP_POSITIVE_Z
GL_TEXTURE_MAG_FILTER GL_TEXTURE_MIN_FILTER GL_TEXTURE_WRAP_S
GL_TEXTURE_WRAP_T GL_TRIANGLES GL_TRIANGLE_FAN GL_TRIANGLE_STRIP GL_TRUE
GL_UNPACK_ALIGNMENT GL_UNSIGNED_BYTE GL_UNSIGNED_INT GL_UNSIGNED_SHORT
GL_UNSIGNED_SHORT_4_4_4_4 GL_UNSIGNED_SHORT_5_5_5_1
GL_UNSIGNED_SHORT_5_6_5 GL_VALIDATE_STATUS GL_VENDOR GL_VERSION
GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING GL_VERTEX_ATTRIB_ARRAY_ENABLED
GL_VERTEX_ATTRIB_ARRAY_NORMALIZED GL_VERTEX_ATTRIB_ARRAY_POINTER
GL_VERTEX_ATTRIB_ARRAY_SIZE GL_VERTEX_ATTRIB_ARRAY_STRIDE
GL_VERTEX_ATTRIB_ARRAY_TYPE GL_VERTEX_SHADER GL_VIEWPORT GL_ZERO
""".replace('\n', ' ')

# vispy_ext.h
constant_names += "GL_MIN GL_MAX"

function_names = [n.strip() for n in function_names.split(' ')]
function_names = set([n for n in function_names if n])
constant_names = [n.strip() for n in constant_names.split(' ')]
constant_names = set([n for n in constant_names if n])
ok_names = set(['gl2', 'glplus'])  # module names

run_tests_if_main()
