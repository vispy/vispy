"""

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Proxy API for GL ES 2.0 subset, via the PyOpenGL library.

"""

import ctypes
from OpenGL import GL
import OpenGL.GL.framebufferobjects as FBO


from OpenGL.GL import glActiveTexture


from OpenGL.GL import glAttachShader


from OpenGL.GL import glBindAttribLocation


from OpenGL.GL import glBindBuffer


from OpenGL.GL.framebufferobjects import glBindFramebuffer


from OpenGL.GL.framebufferobjects import glBindRenderbuffer


from OpenGL.GL import glBindTexture


from OpenGL.GL import glBlendColor


from OpenGL.GL import glBlendEquation


from OpenGL.GL import glBlendEquationSeparate


from OpenGL.GL import glBlendFunc


from OpenGL.GL import glBlendFuncSeparate


def glBufferData(target, data, usage):
    """ Data can be numpy array or the size of data to allocate.
    """
    if isinstance(data, int):
        size = data
        data = None
    else:
        size = data.nbytes
    GL.glBufferData(target, size, data, usage)


def glBufferSubData(target, offset, data):
    size = data.nbytes
    GL.glBufferSubData(target, offset, size, data)


from OpenGL.GL.framebufferobjects import glCheckFramebufferStatus


from OpenGL.GL import glClear


from OpenGL.GL import glClearColor


from OpenGL.GL import glClearDepthf as glClearDepth


from OpenGL.GL import glClearStencil


from OpenGL.GL import glColorMask


from OpenGL.GL import glCompileShader


def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    # border = 0  # set in args
    size = data.size
    GL.glCompressedTexImage2D(target, level, internalformat, width, height, border, size, data)


def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    size = data.size
    GL.glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, size, data)


from OpenGL.GL import glCopyTexImage2D


from OpenGL.GL import glCopyTexSubImage2D


from OpenGL.GL import glCreateProgram


from OpenGL.GL import glCreateShader


from OpenGL.GL import glCullFace


def glDeleteBuffer(buffer):
    GL.glDeleteBuffers(1, [buffer])


def glDeleteFramebuffer(framebuffer):
    FBO.glDeleteFramebuffers(1, [framebuffer])


from OpenGL.GL import glDeleteProgram


def glDeleteRenderbuffer(renderbuffer):
    FBO.glDeleteRenderbuffers(1, [renderbuffer])


from OpenGL.GL import glDeleteShader


def glDeleteTexture(texture):
    GL.glDeleteTextures([texture])


from OpenGL.GL import glDepthFunc


from OpenGL.GL import glDepthMask


from OpenGL.GL import glDepthRangef as glDepthRange


from OpenGL.GL import glDetachShader


from OpenGL.GL import glDisable


from OpenGL.GL import glDisableVertexAttribArray


from OpenGL.GL import glDrawArrays


from OpenGL.GL import glDrawElements


from OpenGL.GL import glEnable


from OpenGL.GL import glEnableVertexAttribArray


from OpenGL.GL import glFinish


from OpenGL.GL import glFlush


from OpenGL.GL.framebufferobjects import glFramebufferRenderbuffer


from OpenGL.GL.framebufferobjects import glFramebufferTexture2D


from OpenGL.GL import glFrontFace


def glCreateBuffer():
    return GL.glGenBuffers(1)


def glCreateFramebuffer():
    return FBO.glGenFramebuffers(1)


def glCreateRenderbuffer():
    return FBO.glGenRenderbuffers(1)


def glCreateTexture():
    return GL.glGenTextures(1)


from OpenGL.GL import glGenerateMipmap


def glGetActiveAttrib(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    # pyopengl has a bug, this is a patch
    GL.glGetActiveAttrib(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


def glGetActiveUniform(program, index):
    name, size, type = GL.glGetActiveUniform(program, index)
    return name.decode('utf-8'), size, type


from OpenGL.GL import glGetAttachedShaders


def glGetAttribLocation(program, name):
    name = name.encode('utf-8')
    return GL.glGetAttribLocation(program, name)


from OpenGL.GL import glGetBooleanv as _glGetBooleanv


from OpenGL.GL import glGetBufferParameteriv as glGetBufferParameter


from OpenGL.GL import glGetError


from OpenGL.GL import glGetFloatv as _glGetFloatv


from OpenGL.GL.framebufferobjects import glGetFramebufferAttachmentParameteriv as glGetFramebufferAttachmentParameter


from OpenGL.GL import glGetIntegerv as _glGetIntegerv


from OpenGL.GL import glGetProgramInfoLog


from OpenGL.GL import glGetProgramiv as glGetProgramParameter


from OpenGL.GL.framebufferobjects import glGetRenderbufferParameteriv as glGetRenderbufferParameter


from OpenGL.GL import glGetShaderInfoLog


from OpenGL.GL import glGetShaderPrecisionFormat


from OpenGL.GL import glGetShaderSource


from OpenGL.GL import glGetShaderiv as glGetShaderParameter


def glGetParameter(pname):
    if pname in [33902, 33901, 32773, 3106, 2931, 2928,
                 2849, 32824, 10752, 32938]:
        # GL_ALIASED_LINE_WIDTH_RANGE GL_ALIASED_POINT_SIZE_RANGE
        # GL_BLEND_COLOR GL_COLOR_CLEAR_VALUE GL_DEPTH_CLEAR_VALUE
        # GL_DEPTH_RANGE GL_LINE_WIDTH GL_POLYGON_OFFSET_FACTOR
        # GL_POLYGON_OFFSET_UNITS GL_SAMPLE_COVERAGE_VALUE
        return _glGetFloatv(pname)
    elif pname in [7936, 7937, 7938, 35724, 7939]:
        # GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION,
        # GL_EXTENSIONS are strings
        pass  # string handled below
    else:
        return _glGetIntegerv(pname)
    name = pname
    return GL.glGetString(pname)


def glGetTexParameter(target, pname):
    n = 1
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    return GL.glGetTexParameterfv(target, pname)
    return params[0]


from OpenGL.GL import glGetUniformfv as glGetUniform


def glGetUniformLocation(program, name):
    name = name.encode('utf-8')
    return GL.glGetUniformLocation(program, name)


def glGetVertexAttrib(program, location):
    n = 4
    d = float('Inf')
    values = (ctypes.c_float*n)(*[d for i in range(n)])
    return GL.glGetVertexAttribfv(program, location)
    values = [p for p in values if p!=d]
    if len(values) == 1:
        return values[0]
    else:
        return values


from OpenGL.GL import glGetVertexAttribPointerv as glGetVertexAttribOffset


from OpenGL.GL import glHint


from OpenGL.GL import glIsBuffer


from OpenGL.GL import glIsEnabled


from OpenGL.GL.framebufferobjects import glIsFramebuffer


from OpenGL.GL import glIsProgram


from OpenGL.GL.framebufferobjects import glIsRenderbuffer


from OpenGL.GL import glIsShader


from OpenGL.GL import glIsTexture


from OpenGL.GL import glLineWidth


from OpenGL.GL import glLinkProgram


from OpenGL.GL import glPixelStorei


from OpenGL.GL import glPolygonOffset


from OpenGL.GL import glReadPixels


from OpenGL.GL.framebufferobjects import glRenderbufferStorage


from OpenGL.GL import glSampleCoverage


from OpenGL.GL import glScissor


def glShaderSource(shader, source):
    # Some implementation do not like getting a list of single chars
    if isinstance(source, (tuple, list)):
        strings = [s for s in source]
    else:
        strings = [source]
    GL.glShaderSource(shader, strings)


from OpenGL.GL import glStencilFunc


from OpenGL.GL import glStencilFuncSeparate


from OpenGL.GL import glStencilMask


from OpenGL.GL import glStencilMaskSeparate


from OpenGL.GL import glStencilOp


from OpenGL.GL import glStencilOpSeparate


def glTexImage2D(target, level, internalformat, format, type, pixels):
    border = 0
    if isinstance(pixels, (tuple, list)):
        height, width = pixels
        pixels = None
    else:
        height, width = pixels.shape[:2]
    GL.glTexImage2D(target, level, internalformat, width, height, border, format, type, pixels)


from OpenGL.GL import glTexParameterf
from OpenGL.GL import glTexParameteri


def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    height, width = pixels.shape[:2]
    GL.glTexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels)


from OpenGL.GL import glUniform1f
from OpenGL.GL import glUniform2f
from OpenGL.GL import glUniform3f
from OpenGL.GL import glUniform4f
from OpenGL.GL import glUniform1i
from OpenGL.GL import glUniform2i
from OpenGL.GL import glUniform3i
from OpenGL.GL import glUniform4i
from OpenGL.GL import glUniform1fv
from OpenGL.GL import glUniform2fv
from OpenGL.GL import glUniform3fv
from OpenGL.GL import glUniform4fv
from OpenGL.GL import glUniform1iv
from OpenGL.GL import glUniform2iv
from OpenGL.GL import glUniform3iv
from OpenGL.GL import glUniform4iv


from OpenGL.GL import glUniformMatrix2fv
from OpenGL.GL import glUniformMatrix3fv
from OpenGL.GL import glUniformMatrix4fv


from OpenGL.GL import glUseProgram


from OpenGL.GL import glValidateProgram


from OpenGL.GL import glVertexAttrib1f
from OpenGL.GL import glVertexAttrib2f
from OpenGL.GL import glVertexAttrib3f
from OpenGL.GL import glVertexAttrib4f


from OpenGL.GL import glVertexAttribPointer


from OpenGL.GL import glViewport


