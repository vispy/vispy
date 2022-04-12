"""GL definitions converted to Python by codegen/createglapi.py.

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

GL ES 2.0 API (via Angle/DirectX on Windows)

"""

import ctypes
from .es2 import _lib


_lib.glActiveTexture.argtypes = ctypes.c_uint,
# void = glActiveTexture(GLenum texture)
def glActiveTexture(texture):
    _lib.glActiveTexture(texture)


_lib.glAttachShader.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glAttachShader(GLuint program, GLuint shader)
def glAttachShader(program, shader):
    _lib.glAttachShader(program, shader)


_lib.glBindAttribLocation.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p,
# void = glBindAttribLocation(GLuint program, GLuint index, GLchar* name)
def glBindAttribLocation(program, index, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    res = _lib.glBindAttribLocation(program, index, name)


_lib.glBindBuffer.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBindBuffer(GLenum target, GLuint buffer)
def glBindBuffer(target, buffer):
    _lib.glBindBuffer(target, buffer)


_lib.glBindFramebuffer.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBindFramebuffer(GLenum target, GLuint framebuffer)
def glBindFramebuffer(target, framebuffer):
    _lib.glBindFramebuffer(target, framebuffer)


_lib.glBindRenderbuffer.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBindRenderbuffer(GLenum target, GLuint renderbuffer)
def glBindRenderbuffer(target, renderbuffer):
    _lib.glBindRenderbuffer(target, renderbuffer)


_lib.glBindTexture.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBindTexture(GLenum target, GLuint texture)
def glBindTexture(target, texture):
    _lib.glBindTexture(target, texture)


_lib.glBlendColor.argtypes = ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
# void = glBlendColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glBlendColor(red, green, blue, alpha):
    _lib.glBlendColor(red, green, blue, alpha)


_lib.glBlendEquation.argtypes = ctypes.c_uint,
# void = glBlendEquation(GLenum mode)
def glBlendEquation(mode):
    _lib.glBlendEquation(mode)


_lib.glBlendEquationSeparate.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBlendEquationSeparate(GLenum modeRGB, GLenum modeAlpha)
def glBlendEquationSeparate(modeRGB, modeAlpha):
    _lib.glBlendEquationSeparate(modeRGB, modeAlpha)


_lib.glBlendFunc.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glBlendFunc(GLenum sfactor, GLenum dfactor)
def glBlendFunc(sfactor, dfactor):
    _lib.glBlendFunc(sfactor, dfactor)


_lib.glBlendFuncSeparate.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
# void = glBlendFuncSeparate(GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha, GLenum dstAlpha)
def glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha):
    _lib.glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha)


_lib.glBufferData.argtypes = ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint,
# void = glBufferData(GLenum target, GLsizeiptr size, GLvoid* data, GLenum usage)
def glBufferData(target, data, usage):
    """Data can be numpy array or the size of data to allocate."""
    if isinstance(data, int):
        size = data
        data = ctypes.c_voidp(0)
    else:
        if not data.flags['C_CONTIGUOUS'] or not data.flags['ALIGNED']:
            data = data.copy('C')
        data_ = data
        size = data_.nbytes
        data = data_.ctypes.data
    res = _lib.glBufferData(target, size, data, usage)


_lib.glBufferSubData.argtypes = ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_void_p,
# void = glBufferSubData(GLenum target, GLintptr offset, GLsizeiptr size, GLvoid* data)
def glBufferSubData(target, offset, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.nbytes
    data = data_.ctypes.data
    res = _lib.glBufferSubData(target, offset, size, data)


_lib.glCheckFramebufferStatus.argtypes = ctypes.c_uint,
_lib.glCheckFramebufferStatus.restype = ctypes.c_uint
# GLenum = glCheckFramebufferStatus(GLenum target)
def glCheckFramebufferStatus(target):
    return _lib.glCheckFramebufferStatus(target)


_lib.glClear.argtypes = ctypes.c_uint,
# void = glClear(GLbitfield mask)
def glClear(mask):
    _lib.glClear(mask)


_lib.glClearColor.argtypes = ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
# void = glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glClearColor(red, green, blue, alpha):
    _lib.glClearColor(red, green, blue, alpha)


_lib.glClearDepthf.argtypes = ctypes.c_float,
# void = glClearDepthf(GLclampf depth)
def glClearDepth(depth):
    _lib.glClearDepthf(depth)


_lib.glClearStencil.argtypes = ctypes.c_int,
# void = glClearStencil(GLint s)
def glClearStencil(s):
    _lib.glClearStencil(s)


_lib.glColorMask.argtypes = ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool,
# void = glColorMask(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
def glColorMask(red, green, blue, alpha):
    _lib.glColorMask(red, green, blue, alpha)


_lib.glCompileShader.argtypes = ctypes.c_uint,
# void = glCompileShader(GLuint shader)
def glCompileShader(shader):
    _lib.glCompileShader(shader)


_lib.glCompressedTexImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,
# void = glCompressedTexImage2D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize, GLvoid* data)
def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    # border = 0  # set in args
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    res = _lib.glCompressedTexImage2D(target, level, internalformat, width, height, border, imageSize, data)


_lib.glCompressedTexSubImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p,
# void = glCompressedTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize, GLvoid* data)
def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    res = _lib.glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, imageSize, data)


_lib.glCopyTexImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
# void = glCopyTexImage2D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
def glCopyTexImage2D(target, level, internalformat, x, y, width, height, border):
    _lib.glCopyTexImage2D(target, level, internalformat, x, y, width, height, border)


_lib.glCopyTexSubImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
# void = glCopyTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
def glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height):
    _lib.glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height)


_lib.glCreateProgram.argtypes = ()
_lib.glCreateProgram.restype = ctypes.c_uint
# GLuint = glCreateProgram()
def glCreateProgram():
    return _lib.glCreateProgram()


_lib.glCreateShader.argtypes = ctypes.c_uint,
_lib.glCreateShader.restype = ctypes.c_uint
# GLuint = glCreateShader(GLenum type)
def glCreateShader(type):
    return _lib.glCreateShader(type)


_lib.glCullFace.argtypes = ctypes.c_uint,
# void = glCullFace(GLenum mode)
def glCullFace(mode):
    _lib.glCullFace(mode)


_lib.glDeleteBuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glDeleteBuffers(GLsizei n, GLuint* buffers)
def glDeleteBuffer(buffer):
    n = 1
    buffers = (ctypes.c_uint*n)(buffer)
    res = _lib.glDeleteBuffers(n, buffers)


_lib.glDeleteFramebuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glDeleteFramebuffers(GLsizei n, GLuint* framebuffers)
def glDeleteFramebuffer(framebuffer):
    n = 1
    framebuffers = (ctypes.c_uint*n)(framebuffer)
    res = _lib.glDeleteFramebuffers(n, framebuffers)


_lib.glDeleteProgram.argtypes = ctypes.c_uint,
# void = glDeleteProgram(GLuint program)
def glDeleteProgram(program):
    _lib.glDeleteProgram(program)


_lib.glDeleteRenderbuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glDeleteRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glDeleteRenderbuffer(renderbuffer):
    n = 1
    renderbuffers = (ctypes.c_uint*n)(renderbuffer)
    res = _lib.glDeleteRenderbuffers(n, renderbuffers)


_lib.glDeleteShader.argtypes = ctypes.c_uint,
# void = glDeleteShader(GLuint shader)
def glDeleteShader(shader):
    _lib.glDeleteShader(shader)


_lib.glDeleteTextures.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glDeleteTextures(GLsizei n, GLuint* textures)
def glDeleteTexture(texture):
    n = 1
    textures = (ctypes.c_uint*n)(texture)
    res = _lib.glDeleteTextures(n, textures)


_lib.glDepthFunc.argtypes = ctypes.c_uint,
# void = glDepthFunc(GLenum func)
def glDepthFunc(func):
    _lib.glDepthFunc(func)


_lib.glDepthMask.argtypes = ctypes.c_bool,
# void = glDepthMask(GLboolean flag)
def glDepthMask(flag):
    _lib.glDepthMask(flag)


_lib.glDepthRangef.argtypes = ctypes.c_float, ctypes.c_float,
# void = glDepthRangef(GLclampf zNear, GLclampf zFar)
def glDepthRange(zNear, zFar):
    _lib.glDepthRangef(zNear, zFar)


_lib.glDetachShader.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glDetachShader(GLuint program, GLuint shader)
def glDetachShader(program, shader):
    _lib.glDetachShader(program, shader)


_lib.glDisable.argtypes = ctypes.c_uint,
# void = glDisable(GLenum cap)
def glDisable(cap):
    _lib.glDisable(cap)


_lib.glDisableVertexAttribArray.argtypes = ctypes.c_uint,
# void = glDisableVertexAttribArray(GLuint index)
def glDisableVertexAttribArray(index):
    _lib.glDisableVertexAttribArray(index)


_lib.glDrawArrays.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_int,
# void = glDrawArrays(GLenum mode, GLint first, GLsizei count)
def glDrawArrays(mode, first, count):
    _lib.glDrawArrays(mode, first, count)


_lib.glDrawElements.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p,
# void = glDrawElements(GLenum mode, GLsizei count, GLenum type, GLvoid* indices)
def glDrawElements(mode, count, type, offset):
    if offset is None:
        offset = ctypes.c_void_p(0)
    elif isinstance(offset, ctypes.c_void_p):
        pass
    elif isinstance(offset, (int, ctypes.c_int)):
        offset = ctypes.c_void_p(int(offset))
    else:
        if not offset.flags['C_CONTIGUOUS']:
            offset = offset.copy('C')
        offset_ = offset
        offset = offset.ctypes.data
    indices = offset
    res = _lib.glDrawElements(mode, count, type, indices)


_lib.glEnable.argtypes = ctypes.c_uint,
# void = glEnable(GLenum cap)
def glEnable(cap):
    _lib.glEnable(cap)


_lib.glEnableVertexAttribArray.argtypes = ctypes.c_uint,
# void = glEnableVertexAttribArray(GLuint index)
def glEnableVertexAttribArray(index):
    _lib.glEnableVertexAttribArray(index)


_lib.glFinish.argtypes = ()
# void = glFinish()
def glFinish():
    _lib.glFinish()


_lib.glFlush.argtypes = ()
# void = glFlush()
def glFlush():
    _lib.glFlush()


_lib.glFramebufferRenderbuffer.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
# void = glFramebufferRenderbuffer(GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer)
def glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer):
    _lib.glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer)


_lib.glFramebufferTexture2D.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_int,
# void = glFramebufferTexture2D(GLenum target, GLenum attachment, GLenum textarget, GLuint texture, GLint level)
def glFramebufferTexture2D(target, attachment, textarget, texture, level):
    _lib.glFramebufferTexture2D(target, attachment, textarget, texture, level)


_lib.glFrontFace.argtypes = ctypes.c_uint,
# void = glFrontFace(GLenum mode)
def glFrontFace(mode):
    _lib.glFrontFace(mode)


_lib.glGenBuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glGenBuffers(GLsizei n, GLuint* buffers)
def glCreateBuffer():
    n = 1
    buffers = (ctypes.c_uint*n)()
    res = _lib.glGenBuffers(n, buffers)
    return buffers[0]


_lib.glGenFramebuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glGenFramebuffers(GLsizei n, GLuint* framebuffers)
def glCreateFramebuffer():
    n = 1
    framebuffers = (ctypes.c_uint*n)()
    res = _lib.glGenFramebuffers(n, framebuffers)
    return framebuffers[0]


_lib.glGenRenderbuffers.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glGenRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glCreateRenderbuffer():
    n = 1
    renderbuffers = (ctypes.c_uint*n)()
    res = _lib.glGenRenderbuffers(n, renderbuffers)
    return renderbuffers[0]


_lib.glGenTextures.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
# void = glGenTextures(GLsizei n, GLuint* textures)
def glCreateTexture():
    n = 1
    textures = (ctypes.c_uint*n)()
    res = _lib.glGenTextures(n, textures)
    return textures[0]


_lib.glGenerateMipmap.argtypes = ctypes.c_uint,
# void = glGenerateMipmap(GLenum target)
def glGenerateMipmap(target):
    _lib.glGenerateMipmap(target)


_lib.glGetActiveAttrib.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
# void = glGetActiveAttrib(GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name)
def glGetActiveAttrib(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    res = _lib.glGetActiveAttrib(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


_lib.glGetActiveUniform.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
# void = glGetActiveUniform(GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name)
def glGetActiveUniform(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    res = _lib.glGetActiveUniform(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


_lib.glGetAttachedShaders.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint),
# void = glGetAttachedShaders(GLuint program, GLsizei maxcount, GLsizei* count, GLuint* shaders)
def glGetAttachedShaders(program):
    maxcount = 256
    count = (ctypes.c_int*1)()
    shaders = (ctypes.c_uint*maxcount)()
    res = _lib.glGetAttachedShaders(program, maxcount, count, shaders)
    return tuple(shaders[:count[0]])


_lib.glGetAttribLocation.argtypes = ctypes.c_uint, ctypes.c_char_p,
_lib.glGetAttribLocation.restype = ctypes.c_int
# GLint = glGetAttribLocation(GLuint program, GLchar* name)
def glGetAttribLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    res = _lib.glGetAttribLocation(program, name)
    return res


_lib.glGetBooleanv.argtypes = ctypes.c_uint, ctypes.POINTER(ctypes.c_bool),
# void = glGetBooleanv(GLenum pname, GLboolean* params)
def _glGetBooleanv(pname):
    params = (ctypes.c_bool*1)()
    res = _lib.glGetBooleanv(pname, params)
    return params[0]


_lib.glGetBufferParameteriv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetBufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetBufferParameter(target, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    res = _lib.glGetBufferParameteriv(target, pname, params)
    return params[0]


_lib.glGetError.argtypes = ()
_lib.glGetError.restype = ctypes.c_uint
# GLenum = glGetError()
def glGetError():
    return _lib.glGetError()


_lib.glGetFloatv.argtypes = ctypes.c_uint, ctypes.POINTER(ctypes.c_float),
# void = glGetFloatv(GLenum pname, GLfloat* params)
def _glGetFloatv(pname):
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    res = _lib.glGetFloatv(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


_lib.glGetFramebufferAttachmentParameteriv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetFramebufferAttachmentParameteriv(GLenum target, GLenum attachment, GLenum pname, GLint* params)
def glGetFramebufferAttachmentParameter(target, attachment, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    res = _lib.glGetFramebufferAttachmentParameteriv(target, attachment, pname, params)
    return params[0]


_lib.glGetIntegerv.argtypes = ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetIntegerv(GLenum pname, GLint* params)
def _glGetIntegerv(pname):
    n = 16
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*n)(*[d for i in range(n)])
    res = _lib.glGetIntegerv(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


_lib.glGetProgramInfoLog.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,
# void = glGetProgramInfoLog(GLuint program, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetProgramInfoLog(program):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    res = _lib.glGetProgramInfoLog(program, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


_lib.glGetProgramiv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetProgramiv(GLuint program, GLenum pname, GLint* params)
def glGetProgramParameter(program, pname):
    params = (ctypes.c_int*1)()
    res = _lib.glGetProgramiv(program, pname, params)
    return params[0]


_lib.glGetRenderbufferParameteriv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetRenderbufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetRenderbufferParameter(target, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    res = _lib.glGetRenderbufferParameteriv(target, pname, params)
    return params[0]


_lib.glGetShaderInfoLog.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,
# void = glGetShaderInfoLog(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetShaderInfoLog(shader):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    res = _lib.glGetShaderInfoLog(shader, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


_lib.glGetShaderPrecisionFormat.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
# void = glGetShaderPrecisionFormat(GLenum shadertype, GLenum precisiontype, GLint* range, GLint* precision)
def glGetShaderPrecisionFormat(shadertype, precisiontype):
    range = (ctypes.c_int*1)()
    precision = (ctypes.c_int*1)()
    res = _lib.glGetShaderPrecisionFormat(shadertype, precisiontype, range, precision)
    return range[0], precision[0]


_lib.glGetShaderSource.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,
# void = glGetShaderSource(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* source)
def glGetShaderSource(shader):
    bufsize = 1024*1024
    length = (ctypes.c_int*1)()
    source = (ctypes.c_char*bufsize)()
    res = _lib.glGetShaderSource(shader, bufsize, length, source)
    return source.value[:length[0]].decode('utf-8')


_lib.glGetShaderiv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),
# void = glGetShaderiv(GLuint shader, GLenum pname, GLint* params)
def glGetShaderParameter(shader, pname):
    params = (ctypes.c_int*1)()
    res = _lib.glGetShaderiv(shader, pname, params)
    return params[0]


_lib.glGetString.argtypes = ctypes.c_uint,
_lib.glGetString.restype = ctypes.c_char_p
# GLubyte* = glGetString(GLenum name)
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
    res = _lib.glGetString(name)
    return ctypes.string_at(res).decode('utf-8') if res else ''


_lib.glGetTexParameterfv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),
# void = glGetTexParameterfv(GLenum target, GLenum pname, GLfloat* params)
def glGetTexParameter(target, pname):
    d = float('Inf')
    params = (ctypes.c_float*1)(d)
    res = _lib.glGetTexParameterfv(target, pname, params)
    return params[0]


_lib.glGetUniformfv.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
# void = glGetUniformfv(GLuint program, GLint location, GLfloat* params)
def glGetUniform(program, location):
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    res = _lib.glGetUniformfv(program, location, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


_lib.glGetUniformLocation.argtypes = ctypes.c_uint, ctypes.c_char_p,
_lib.glGetUniformLocation.restype = ctypes.c_int
# GLint = glGetUniformLocation(GLuint program, GLchar* name)
def glGetUniformLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    res = _lib.glGetUniformLocation(program, name)
    return res


_lib.glGetVertexAttribfv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),
# void = glGetVertexAttribfv(GLuint index, GLenum pname, GLfloat* params)
def glGetVertexAttrib(index, pname):
    n = 4
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    res = _lib.glGetVertexAttribfv(index, pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


_lib.glGetVertexAttribPointerv.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p),
# void = glGetVertexAttribPointerv(GLuint index, GLenum pname, GLvoid** pointer)
def glGetVertexAttribOffset(index, pname):
    pointer = (ctypes.c_void_p*1)()
    res = _lib.glGetVertexAttribPointerv(index, pname, pointer)
    return pointer[0] or 0


_lib.glHint.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glHint(GLenum target, GLenum mode)
def glHint(target, mode):
    _lib.glHint(target, mode)


_lib.glIsBuffer.argtypes = ctypes.c_uint,
_lib.glIsBuffer.restype = ctypes.c_bool
# GLboolean = glIsBuffer(GLuint buffer)
def glIsBuffer(buffer):
    return _lib.glIsBuffer(buffer)


_lib.glIsEnabled.argtypes = ctypes.c_uint,
_lib.glIsEnabled.restype = ctypes.c_bool
# GLboolean = glIsEnabled(GLenum cap)
def glIsEnabled(cap):
    return _lib.glIsEnabled(cap)


_lib.glIsFramebuffer.argtypes = ctypes.c_uint,
_lib.glIsFramebuffer.restype = ctypes.c_bool
# GLboolean = glIsFramebuffer(GLuint framebuffer)
def glIsFramebuffer(framebuffer):
    return _lib.glIsFramebuffer(framebuffer)


_lib.glIsProgram.argtypes = ctypes.c_uint,
_lib.glIsProgram.restype = ctypes.c_bool
# GLboolean = glIsProgram(GLuint program)
def glIsProgram(program):
    return _lib.glIsProgram(program)


_lib.glIsRenderbuffer.argtypes = ctypes.c_uint,
_lib.glIsRenderbuffer.restype = ctypes.c_bool
# GLboolean = glIsRenderbuffer(GLuint renderbuffer)
def glIsRenderbuffer(renderbuffer):
    return _lib.glIsRenderbuffer(renderbuffer)


_lib.glIsShader.argtypes = ctypes.c_uint,
_lib.glIsShader.restype = ctypes.c_bool
# GLboolean = glIsShader(GLuint shader)
def glIsShader(shader):
    return _lib.glIsShader(shader)


_lib.glIsTexture.argtypes = ctypes.c_uint,
_lib.glIsTexture.restype = ctypes.c_bool
# GLboolean = glIsTexture(GLuint texture)
def glIsTexture(texture):
    return _lib.glIsTexture(texture)


_lib.glLineWidth.argtypes = ctypes.c_float,
# void = glLineWidth(GLfloat width)
def glLineWidth(width):
    _lib.glLineWidth(width)


_lib.glLinkProgram.argtypes = ctypes.c_uint,
# void = glLinkProgram(GLuint program)
def glLinkProgram(program):
    _lib.glLinkProgram(program)


_lib.glPixelStorei.argtypes = ctypes.c_uint, ctypes.c_int,
# void = glPixelStorei(GLenum pname, GLint param)
def glPixelStorei(pname, param):
    _lib.glPixelStorei(pname, param)


_lib.glPolygonOffset.argtypes = ctypes.c_float, ctypes.c_float,
# void = glPolygonOffset(GLfloat factor, GLfloat units)
def glPolygonOffset(factor, units):
    _lib.glPolygonOffset(factor, units)


_lib.glReadPixels.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
# void = glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glReadPixels(x, y, width, height, format, type):
    # GL_ALPHA, GL_RGB, GL_RGBA
    t = {6406:1, 6407:3, 6408:4}[format]
    # GL_UNSIGNED_BYTE, GL_FLOAT
    nb = {5121:1, 5126:4}[type]
    size = int(width*height*t*nb)
    pixels = ctypes.create_string_buffer(size)
    res = _lib.glReadPixels(x, y, width, height, format, type, pixels)
    return pixels[:]


_lib.glRenderbufferStorage.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_int,
# void = glRenderbufferStorage(GLenum target, GLenum internalformat, GLsizei width, GLsizei height)
def glRenderbufferStorage(target, internalformat, width, height):
    _lib.glRenderbufferStorage(target, internalformat, width, height)


_lib.glSampleCoverage.argtypes = ctypes.c_float, ctypes.c_bool,
# void = glSampleCoverage(GLclampf value, GLboolean invert)
def glSampleCoverage(value, invert):
    _lib.glSampleCoverage(value, invert)


_lib.glScissor.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
# void = glScissor(GLint x, GLint y, GLsizei width, GLsizei height)
def glScissor(x, y, width, height):
    _lib.glScissor(x, y, width, height)


_lib.glShaderSource.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int),
# void = glShaderSource(GLuint shader, GLsizei count, GLchar** string, GLint* length)
def glShaderSource(shader, source):
    # Some implementation do not like getting a list of single chars
    if isinstance(source, (tuple, list)):
        strings = [s for s in source]
    else:
        strings = [source]
    count = len(strings)
    string = (ctypes.c_char_p*count)(*[s.encode('utf-8') for s in strings])
    length = (ctypes.c_int*count)(*[len(s) for s in strings])
    res = _lib.glShaderSource(shader, count, string, length)


_lib.glStencilFunc.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_uint,
# void = glStencilFunc(GLenum func, GLint ref, GLuint mask)
def glStencilFunc(func, ref, mask):
    _lib.glStencilFunc(func, ref, mask)


_lib.glStencilFuncSeparate.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint,
# void = glStencilFuncSeparate(GLenum face, GLenum func, GLint ref, GLuint mask)
def glStencilFuncSeparate(face, func, ref, mask):
    _lib.glStencilFuncSeparate(face, func, ref, mask)


_lib.glStencilMask.argtypes = ctypes.c_uint,
# void = glStencilMask(GLuint mask)
def glStencilMask(mask):
    _lib.glStencilMask(mask)


_lib.glStencilMaskSeparate.argtypes = ctypes.c_uint, ctypes.c_uint,
# void = glStencilMaskSeparate(GLenum face, GLuint mask)
def glStencilMaskSeparate(face, mask):
    _lib.glStencilMaskSeparate(face, mask)


_lib.glStencilOp.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
# void = glStencilOp(GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOp(fail, zfail, zpass):
    _lib.glStencilOp(fail, zfail, zpass)


_lib.glStencilOpSeparate.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
# void = glStencilOpSeparate(GLenum face, GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOpSeparate(face, fail, zfail, zpass):
    _lib.glStencilOpSeparate(face, fail, zfail, zpass)


_lib.glTexImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
# void = glTexImage2D(GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid* pixels)
def glTexImage2D(target, level, internalformat, format, type, pixels):
    border = 0
    if isinstance(pixels, (tuple, list)):
        height, width = pixels
        pixels = ctypes.c_void_p(0)
        pixels = None
    else:
        if not pixels.flags['C_CONTIGUOUS']:
            pixels = pixels.copy('C')
        pixels_ = pixels
        pixels = pixels_.ctypes.data
        height, width = pixels_.shape[:2]
    res = _lib.glTexImage2D(target, level, internalformat, width, height, border, format, type, pixels)


_lib.glTexParameterf.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_float,
def glTexParameterf(target, pname, param):
    _lib.glTexParameterf(target, pname, param)
_lib.glTexParameteri.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_int,
def glTexParameteri(target, pname, param):
    _lib.glTexParameteri(target, pname, param)


_lib.glTexSubImage2D.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
# void = glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    if not pixels.flags['C_CONTIGUOUS']:
        pixels = pixels.copy('C')
    pixels_ = pixels
    pixels = pixels_.ctypes.data
    height, width = pixels_.shape[:2]
    res = _lib.glTexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels)


_lib.glUniform1f.argtypes = ctypes.c_int, ctypes.c_float,
def glUniform1f(location, v1):
    _lib.glUniform1f(location, v1)
_lib.glUniform2f.argtypes = ctypes.c_int, ctypes.c_float, ctypes.c_float,
def glUniform2f(location, v1, v2):
    _lib.glUniform2f(location, v1, v2)
_lib.glUniform3f.argtypes = ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float,
def glUniform3f(location, v1, v2, v3):
    _lib.glUniform3f(location, v1, v2, v3)
_lib.glUniform4f.argtypes = ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
def glUniform4f(location, v1, v2, v3, v4):
    _lib.glUniform4f(location, v1, v2, v3, v4)
_lib.glUniform1i.argtypes = ctypes.c_int, ctypes.c_int,
def glUniform1i(location, v1):
    _lib.glUniform1i(location, v1)
_lib.glUniform2i.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int,
def glUniform2i(location, v1, v2):
    _lib.glUniform2i(location, v1, v2)
_lib.glUniform3i.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
def glUniform3i(location, v1, v2, v3):
    _lib.glUniform3i(location, v1, v2, v3)
_lib.glUniform4i.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
def glUniform4i(location, v1, v2, v3, v4):
    _lib.glUniform4i(location, v1, v2, v3, v4)
_lib.glUniform1fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
def glUniform1fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    _lib.glUniform1fv(location, count, values)
_lib.glUniform2fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
def glUniform2fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    _lib.glUniform2fv(location, count, values)
_lib.glUniform3fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
def glUniform3fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    _lib.glUniform3fv(location, count, values)
_lib.glUniform4fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
def glUniform4fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    _lib.glUniform4fv(location, count, values)
_lib.glUniform1iv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
def glUniform1iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    _lib.glUniform1iv(location, count, values)
_lib.glUniform2iv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
def glUniform2iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    _lib.glUniform2iv(location, count, values)
_lib.glUniform3iv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
def glUniform3iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    _lib.glUniform3iv(location, count, values)
_lib.glUniform4iv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
def glUniform4iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    _lib.glUniform4iv(location, count, values)


_lib.glUniformMatrix2fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),
def glUniformMatrix2fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    _lib.glUniformMatrix2fv(location, count, transpose, values)
_lib.glUniformMatrix3fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),
def glUniformMatrix3fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    _lib.glUniformMatrix3fv(location, count, transpose, values)
_lib.glUniformMatrix4fv.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),
def glUniformMatrix4fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    _lib.glUniformMatrix4fv(location, count, transpose, values)


_lib.glUseProgram.argtypes = ctypes.c_uint,
# void = glUseProgram(GLuint program)
def glUseProgram(program):
    _lib.glUseProgram(program)


_lib.glValidateProgram.argtypes = ctypes.c_uint,
# void = glValidateProgram(GLuint program)
def glValidateProgram(program):
    _lib.glValidateProgram(program)


_lib.glVertexAttrib1f.argtypes = ctypes.c_uint, ctypes.c_float,
def glVertexAttrib1f(index, v1):
    _lib.glVertexAttrib1f(index, v1)
_lib.glVertexAttrib2f.argtypes = ctypes.c_uint, ctypes.c_float, ctypes.c_float,
def glVertexAttrib2f(index, v1, v2):
    _lib.glVertexAttrib2f(index, v1, v2)
_lib.glVertexAttrib3f.argtypes = ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float,
def glVertexAttrib3f(index, v1, v2, v3):
    _lib.glVertexAttrib3f(index, v1, v2, v3)
_lib.glVertexAttrib4f.argtypes = ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
def glVertexAttrib4f(index, v1, v2, v3, v4):
    _lib.glVertexAttrib4f(index, v1, v2, v3, v4)


_lib.glVertexAttribPointer.argtypes = ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p,
# void = glVertexAttribPointer(GLuint indx, GLint size, GLenum type, GLboolean normalized, GLsizei stride, GLvoid* ptr)
def glVertexAttribPointer(indx, size, type, normalized, stride, offset):
    if offset is None:
        offset = ctypes.c_void_p(0)
    elif isinstance(offset, ctypes.c_void_p):
        pass
    elif isinstance(offset, (int, ctypes.c_int)):
        offset = ctypes.c_void_p(int(offset))
    else:
        if not offset.flags['C_CONTIGUOUS']:
            offset = offset.copy('C')
        offset_ = offset
        offset = offset.ctypes.data
        # We need to ensure that the data exists at draw time :(
        # PyOpenGL does this too
        key = '_vert_attr_'+str(indx)
        setattr(glVertexAttribPointer, key, offset_)
    ptr = offset
    res = _lib.glVertexAttribPointer(indx, size, type, normalized, stride, ptr)


_lib.glViewport.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
# void = glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
def glViewport(x, y, width, height):
    _lib.glViewport(x, y, width, height)


