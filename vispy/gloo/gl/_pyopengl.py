"""

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Proxy API for GL ES 2.0 subset, via the PyOpenGL library.

"""

import ctypes
from OpenGL import GL
import OpenGL.GL.framebufferobjects as FBO


def glActiveTexture(texture):
    return GL.glActiveTexture(texture)


def glAttachShader(program, shader):
    return GL.glAttachShader(program, shader)


def glBindAttribLocation(program, index, name):
    return GL.glBindAttribLocation(program, index, name)


def glBindBuffer(target, buffer):
    return GL.glBindBuffer(target, buffer)


def glBindFramebuffer(target, framebuffer):
    return FBO.glBindFramebuffer(target, framebuffer)


def glBindRenderbuffer(target, renderbuffer):
    return FBO.glBindRenderbuffer(target, renderbuffer)


def glBindTexture(target, texture):
    return GL.glBindTexture(target, texture)


def glBlendColor(red, green, blue, alpha):
    return GL.glBlendColor(red, green, blue, alpha)


def glBlendEquation(mode):
    return GL.glBlendEquation(mode)


def glBlendEquationSeparate(modeRGB, modeAlpha):
    return GL.glBlendEquationSeparate(modeRGB, modeAlpha)


def glBlendFunc(sfactor, dfactor):
    return GL.glBlendFunc(sfactor, dfactor)


def glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha):
    return GL.glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha)


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


def glCheckFramebufferStatus(target):
    return FBO.glCheckFramebufferStatus(target)


def glClear(mask):
    return GL.glClear(mask)


def glClearColor(red, green, blue, alpha):
    return GL.glClearColor(red, green, blue, alpha)


def glClearDepth(depth):
    return GL.glClearDepthf(depth)


def glClearStencil(s):
    return GL.glClearStencil(s)


def glColorMask(red, green, blue, alpha):
    return GL.glColorMask(red, green, blue, alpha)


def glCompileShader(shader):
    return GL.glCompileShader(shader)


def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    # border = 0  # set in args
    size = data.size
    GL.glCompressedTexImage2D(target, level, internalformat, width, height, border, size, data)


def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    size = data.size
    GL.glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, size, data)


def glCopyTexImage2D(target, level, internalformat, x, y, width, height, border):
    return GL.glCopyTexImage2D(target, level, internalformat, x, y, width, height, border)


def glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height):
    return GL.glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height)


def glCreateProgram():
    return GL.glCreateProgram()


def glCreateShader(type):
    return GL.glCreateShader(type)


def glCullFace(mode):
    return GL.glCullFace(mode)


def glDeleteBuffer(buffer):
    GL.glDeleteBuffers([buffer])


def glDeleteFramebuffer(framebuffer):
    FBO.glDeleteFrameBuffers([framebuffer])


def glDeleteProgram(program):
    return GL.glDeleteProgram(program)


def glDeleteRenderbuffer(renderbuffer):
    FBO.glDeleteRenderbuffers([renderbuffer])


def glDeleteShader(shader):
    return GL.glDeleteShader(shader)


def glDeleteTexture(texture):
    GL.glDeleteTextures([texture])


def glDepthFunc(func):
    return GL.glDepthFunc(func)


def glDepthMask(flag):
    return GL.glDepthMask(flag)


def glDepthRange(zNear, zFar):
    return GL.glDepthRangef(zNear, zFar)


def glDetachShader(program, shader):
    return GL.glDetachShader(program, shader)


def glDisable(cap):
    return GL.glDisable(cap)


def glDisableVertexAttribArray(index):
    return GL.glDisableVertexAttribArray(index)


def glDrawArrays(mode, first, count):
    return GL.glDrawArrays(mode, first, count)


def glDrawElements(mode, count, type, offset):
    """ offset can be integer offset or array of indices.
    """


def glEnable(cap):
    return GL.glEnable(cap)


def glEnableVertexAttribArray(index):
    return GL.glEnableVertexAttribArray(index)


def glFinish():
    return GL.glFinish()


def glFlush():
    return GL.glFlush()


def glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer):
    return FBO.glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer)


def glFramebufferTexture2D(target, attachment, textarget, texture, level):
    return FBO.glFramebufferTexture2D(target, attachment, textarget, texture, level)


def glFrontFace(mode):
    return GL.glFrontFace(mode)


def glCreateBuffer():
    return GL.glGenBuffers(1)


def glCreateFramebuffer():
    return FBO.glGenFrameBuffers(1)


def glCreateRenderbuffer():
    return FBO.glGenRenderbuffers(1)


def glCreateTexture():
    return GL.glGenTextures(1)


def glGenerateMipmap(target):
    return GL.glGenerateMipmap(target)


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


def glGetAttachedShaders(program):
    return GL.glGetAttachedShaders(program)


def glGetAttribLocation(program, name):
    name = name.encode('utf-8')
    return GL.glGetAttribLocation(program, name)


def _glGetBooleanv(pname):
    return GL.glGetBooleanv(pname)


def glGetBufferParameter(target, pname):
    return GL.glGetBufferParameteriv(target, pname)


def glGetError():
    return GL.glGetError()


def _glGetFloatv(pname):
    return GL.glGetFloatv(pname)


def glGetFramebufferAttachmentParameter(target, attachment, pname):
    return FBO.glGetFramebufferAttachmentParameteriv(target, attachment, pname)


def _glGetIntegerv(pname):
    return GL.glGetIntegerv(pname)


def glGetProgramInfoLog(program):
    return GL.glGetProgramInfoLog(program)


def glGetProgramParameter(program, pname):
    return GL.glGetProgramiv(program, pname)


def glGetRenderbufferParameter(target, pname):
    return FBO.glGetRenderbufferParameteriv(target, pname)


def glGetShaderInfoLog(shader):
    return GL.glGetShaderInfoLog(shader)


def glGetShaderPrecisionFormat(shadertype, precisiontype):
    return GL.glGetShaderPrecisionFormat(shadertype, precisiontype)


def glGetShaderSource(shader):
    return GL.glGetShaderSource(shader)


def glGetShaderParameter(shader, pname):
    return GL.glGetShaderiv(shader, pname)


def glGetParameter(pname):
    # GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION,
    # GL_EXTENSIONS are strings, rest is numbers, gl takes care of
    # type conversion if needed.
    if pname not in [7936, 7937, 7938, 35724, 7939]:
        return _glGetFloatv(pname)
    name = pname
    return GL.glGetString(pname)


def glGetTexParameterfv(target, pname):
    return GL.glGetTexParameterfv(target, pname)
def glGetTexParameteriv(target, pname):
    return GL.glGetTexParameteriv(target, pname)


def glGetUniformfv(program, location):
    return GL.glGetUniformfv(program, location)
def glGetUniformiv(program, location):
    return GL.glGetUniformiv(program, location)


def glGetUniformLocation(program, name):
    name = name.encode('utf-8')
    return GL.glGetUniformLocation(program, name)


def glGetVertexAttribfv(index, pname):
    return GL.glGetVertexAttribfv(index, pname)
def glGetVertexAttribiv(index, pname):
    return GL.glGetVertexAttribiv(index, pname)


def glGetVertexAttribOffset(index, pname):
    return GL.glGetVertexAttribPointerv(index, pname)


def glHint(target, mode):
    return GL.glHint(target, mode)


def glIsBuffer(buffer):
    return GL.glIsBuffer(buffer)


def glIsEnabled(cap):
    return GL.glIsEnabled(cap)


def glIsFramebuffer(framebuffer):
    return FBO.glIsFramebuffer(framebuffer)


def glIsProgram(program):
    return GL.glIsProgram(program)


def glIsRenderbuffer(renderbuffer):
    return FBO.glIsRenderbuffer(renderbuffer)


def glIsShader(shader):
    return GL.glIsShader(shader)


def glIsTexture(texture):
    return GL.glIsTexture(texture)


def glLineWidth(width):
    return GL.glLineWidth(width)


def glLinkProgram(program):
    return GL.glLinkProgram(program)


def glPixelStorei(pname, param):
    return GL.glPixelStorei(pname, param)


def glPolygonOffset(factor, units):
    return GL.glPolygonOffset(factor, units)


def glReadPixels(x, y, width, height, format, type):
    """ Return pixels as bytes.
    """


def glRenderbufferStorage(target, internalformat, width, height):
    return FBO.glRenderbufferStorage(target, internalformat, width, height)


def glSampleCoverage(value, invert):
    return GL.glSampleCoverage(value, invert)


def glScissor(x, y, width, height):
    return GL.glScissor(x, y, width, height)


def glShaderSource(shader, source):
    if isinstance(source, (tuple, list)):
        strings = [s for s in source]
    else:
        strings = [source]
    GL.glShaderSource(shader, strings)


def glStencilFunc(func, ref, mask):
    return GL.glStencilFunc(func, ref, mask)


def glStencilFuncSeparate(face, func, ref, mask):
    return GL.glStencilFuncSeparate(face, func, ref, mask)


def glStencilMask(mask):
    return GL.glStencilMask(mask)


def glStencilMaskSeparate(face, mask):
    return GL.glStencilMaskSeparate(face, mask)


def glStencilOp(fail, zfail, zpass):
    return GL.glStencilOp(fail, zfail, zpass)


def glStencilOpSeparate(face, fail, zfail, zpass):
    return GL.glStencilOpSeparate(face, fail, zfail, zpass)


def glTexImage2D(target, level, internalformat, format, type, pixels):
    border = 0
    if isinstance(pixels, (tuple, list)):
        width, height = pixels
        pixels = None
    else:
        width, height = pixels.shape[:2]
    GL.glTexImage2D(target, level, internalformat, width, height, border, format, type, pixels)


def glTexParameterf(target, pname, param):
    return GL.glTexParameterf(target, pname, param)
def glTexParameteri(target, pname, param):
    return GL.glTexParameteri(target, pname, param)


def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    width, height = pixels.shape[:2]
    GL.glTexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels)


def glUniform1f(location, v1):
    return GL.glUniform1f(location, v1)
def glUniform2f(location, v1, v2):
    return GL.glUniform2f(location, v1, v2)
def glUniform3f(location, v1, v2, v3):
    return GL.glUniform3f(location, v1, v2, v3)
def glUniform4f(location, v1, v2, v3, v4):
    return GL.glUniform4f(location, v1, v2, v3, v4)
def glUniform1i(location, v1):
    return GL.glUniform1i(location, v1)
def glUniform2i(location, v1, v2):
    return GL.glUniform2i(location, v1, v2)
def glUniform3i(location, v1, v2, v3):
    return GL.glUniform3i(location, v1, v2, v3)
def glUniform4i(location, v1, v2, v3, v4):
    return GL.glUniform4i(location, v1, v2, v3, v4)
def glUniform1fv(location, count, values):
    return GL.glUniform1fv(location, count, values)
def glUniform2fv(location, count, values):
    return GL.glUniform2fv(location, count, values)
def glUniform3fv(location, count, values):
    return GL.glUniform3fv(location, count, values)
def glUniform4fv(location, count, values):
    return GL.glUniform4fv(location, count, values)
def glUniform1iv(location, count, values):
    return GL.glUniform1iv(location, count, values)
def glUniform2iv(location, count, values):
    return GL.glUniform2iv(location, count, values)
def glUniform3iv(location, count, values):
    return GL.glUniform3iv(location, count, values)
def glUniform4iv(location, count, values):
    return GL.glUniform4iv(location, count, values)


def glUniformMatrix2fv(location, count, transpose, values):
    return GL.glUniformMatrix2fv(location, count, transpose, values)
def glUniformMatrix3fv(location, count, transpose, values):
    return GL.glUniformMatrix3fv(location, count, transpose, values)
def glUniformMatrix4fv(location, count, transpose, values):
    return GL.glUniformMatrix4fv(location, count, transpose, values)


def glUseProgram(program):
    return GL.glUseProgram(program)


def glValidateProgram(program):
    return GL.glValidateProgram(program)


def glVertexAttrib1f(index, v1):
    return GL.glVertexAttrib1f(index, v1)
def glVertexAttrib2f(index, v1, v2):
    return GL.glVertexAttrib2f(index, v1, v2)
def glVertexAttrib3f(index, v1, v2, v3):
    return GL.glVertexAttrib3f(index, v1, v2, v3)
def glVertexAttrib4f(index, v1, v2, v3, v4):
    return GL.glVertexAttrib4f(index, v1, v2, v3, v4)


def glVertexAttribPointer(indx, size, type, normalized, stride, offset):
    return GL.glVertexAttribPointer(indx, size, type, normalized, stride, offset)


def glViewport(x, y, width, height):
    return GL.glViewport(x, y, width, height)


