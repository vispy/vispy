"""GL definitions converted to Python by codegen/createglapi.py.

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Subset of desktop GL API compatible with GL ES 2.0

"""

import ctypes
from .gl2 import _lib, _get_gl_func


# void = glActiveTexture(GLenum texture)
def glActiveTexture(texture):
    try:
        nativefunc = glActiveTexture._native
    except AttributeError:
        nativefunc = glActiveTexture._native = _get_gl_func("glActiveTexture", None, (ctypes.c_uint,))
    nativefunc(texture)


# void = glAttachShader(GLuint program, GLuint shader)
def glAttachShader(program, shader):
    try:
        nativefunc = glAttachShader._native
    except AttributeError:
        nativefunc = glAttachShader._native = _get_gl_func("glAttachShader", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(program, shader)


# void = glBindAttribLocation(GLuint program, GLuint index, GLchar* name)
def glBindAttribLocation(program, index, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        nativefunc = glBindAttribLocation._native
    except AttributeError:
        nativefunc = glBindAttribLocation._native = _get_gl_func("glBindAttribLocation", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p,))
    res = nativefunc(program, index, name)


# void = glBindBuffer(GLenum target, GLuint buffer)
def glBindBuffer(target, buffer):
    try:
        nativefunc = glBindBuffer._native
    except AttributeError:
        nativefunc = glBindBuffer._native = _get_gl_func("glBindBuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, buffer)


# void = glBindFramebuffer(GLenum target, GLuint framebuffer)
def glBindFramebuffer(target, framebuffer):
    try:
        nativefunc = glBindFramebuffer._native
    except AttributeError:
        nativefunc = glBindFramebuffer._native = _get_gl_func("glBindFramebuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, framebuffer)


# void = glBindRenderbuffer(GLenum target, GLuint renderbuffer)
def glBindRenderbuffer(target, renderbuffer):
    try:
        nativefunc = glBindRenderbuffer._native
    except AttributeError:
        nativefunc = glBindRenderbuffer._native = _get_gl_func("glBindRenderbuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, renderbuffer)


# void = glBindTexture(GLenum target, GLuint texture)
def glBindTexture(target, texture):
    try:
        nativefunc = glBindTexture._native
    except AttributeError:
        nativefunc = glBindTexture._native = _get_gl_func("glBindTexture", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, texture)


# void = glBlendColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glBlendColor(red, green, blue, alpha):
    try:
        nativefunc = glBlendColor._native
    except AttributeError:
        nativefunc = glBlendColor._native = _get_gl_func("glBlendColor", None, (ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(red, green, blue, alpha)


# void = glBlendEquation(GLenum mode)
def glBlendEquation(mode):
    try:
        nativefunc = glBlendEquation._native
    except AttributeError:
        nativefunc = glBlendEquation._native = _get_gl_func("glBlendEquation", None, (ctypes.c_uint,))
    nativefunc(mode)


# void = glBlendEquationSeparate(GLenum modeRGB, GLenum modeAlpha)
def glBlendEquationSeparate(modeRGB, modeAlpha):
    try:
        nativefunc = glBlendEquationSeparate._native
    except AttributeError:
        nativefunc = glBlendEquationSeparate._native = _get_gl_func("glBlendEquationSeparate", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(modeRGB, modeAlpha)


# void = glBlendFunc(GLenum sfactor, GLenum dfactor)
def glBlendFunc(sfactor, dfactor):
    try:
        nativefunc = glBlendFunc._native
    except AttributeError:
        nativefunc = glBlendFunc._native = _get_gl_func("glBlendFunc", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(sfactor, dfactor)


# void = glBlendFuncSeparate(GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha, GLenum dstAlpha)
def glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha):
    try:
        nativefunc = glBlendFuncSeparate._native
    except AttributeError:
        nativefunc = glBlendFuncSeparate._native = _get_gl_func("glBlendFuncSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    nativefunc(srcRGB, dstRGB, srcAlpha, dstAlpha)


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
    try:
        nativefunc = glBufferData._native
    except AttributeError:
        nativefunc = glBufferData._native = _get_gl_func("glBufferData", None, (ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint,))
    res = nativefunc(target, size, data, usage)


# void = glBufferSubData(GLenum target, GLintptr offset, GLsizeiptr size, GLvoid* data)
def glBufferSubData(target, offset, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.nbytes
    data = data_.ctypes.data
    try:
        nativefunc = glBufferSubData._native
    except AttributeError:
        nativefunc = glBufferSubData._native = _get_gl_func("glBufferSubData", None, (ctypes.c_uint, ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_void_p,))
    res = nativefunc(target, offset, size, data)


# GLenum = glCheckFramebufferStatus(GLenum target)
def glCheckFramebufferStatus(target):
    try:
        nativefunc = glCheckFramebufferStatus._native
    except AttributeError:
        nativefunc = glCheckFramebufferStatus._native = _get_gl_func("glCheckFramebufferStatus", ctypes.c_uint, (ctypes.c_uint,))
    return nativefunc(target)


# void = glClear(GLbitfield mask)
def glClear(mask):
    try:
        nativefunc = glClear._native
    except AttributeError:
        nativefunc = glClear._native = _get_gl_func("glClear", None, (ctypes.c_uint,))
    nativefunc(mask)


# void = glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glClearColor(red, green, blue, alpha):
    try:
        nativefunc = glClearColor._native
    except AttributeError:
        nativefunc = glClearColor._native = _get_gl_func("glClearColor", None, (ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(red, green, blue, alpha)


# void = glClearDepthf(GLclampf depth)
def glClearDepth(depth):
    try:
        nativefunc = glClearDepth._native
    except AttributeError:
        nativefunc = glClearDepth._native = _get_gl_func("glClearDepth", None, (ctypes.c_double,))
    nativefunc(depth)


# void = glClearStencil(GLint s)
def glClearStencil(s):
    try:
        nativefunc = glClearStencil._native
    except AttributeError:
        nativefunc = glClearStencil._native = _get_gl_func("glClearStencil", None, (ctypes.c_int,))
    nativefunc(s)


# void = glColorMask(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
def glColorMask(red, green, blue, alpha):
    try:
        nativefunc = glColorMask._native
    except AttributeError:
        nativefunc = glColorMask._native = _get_gl_func("glColorMask", None, (ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool,))
    nativefunc(red, green, blue, alpha)


# void = glCompileShader(GLuint shader)
def glCompileShader(shader):
    try:
        nativefunc = glCompileShader._native
    except AttributeError:
        nativefunc = glCompileShader._native = _get_gl_func("glCompileShader", None, (ctypes.c_uint,))
    nativefunc(shader)


# void = glCompressedTexImage2D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize, GLvoid* data)
def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    # border = 0  # set in args
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    try:
        nativefunc = glCompressedTexImage2D._native
    except AttributeError:
        nativefunc = glCompressedTexImage2D._native = _get_gl_func("glCompressedTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,))
    res = nativefunc(target, level, internalformat, width, height, border, imageSize, data)


# void = glCompressedTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize, GLvoid* data)
def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    try:
        nativefunc = glCompressedTexSubImage2D._native
    except AttributeError:
        nativefunc = glCompressedTexSubImage2D._native = _get_gl_func("glCompressedTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p,))
    res = nativefunc(target, level, xoffset, yoffset, width, height, format, imageSize, data)


# void = glCopyTexImage2D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
def glCopyTexImage2D(target, level, internalformat, x, y, width, height, border):
    try:
        nativefunc = glCopyTexImage2D._native
    except AttributeError:
        nativefunc = glCopyTexImage2D._native = _get_gl_func("glCopyTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(target, level, internalformat, x, y, width, height, border)


# void = glCopyTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
def glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height):
    try:
        nativefunc = glCopyTexSubImage2D._native
    except AttributeError:
        nativefunc = glCopyTexSubImage2D._native = _get_gl_func("glCopyTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(target, level, xoffset, yoffset, x, y, width, height)


# GLuint = glCreateProgram()
def glCreateProgram():
    try:
        nativefunc = glCreateProgram._native
    except AttributeError:
        nativefunc = glCreateProgram._native = _get_gl_func("glCreateProgram", ctypes.c_uint, ())
    return nativefunc()


# GLuint = glCreateShader(GLenum type)
def glCreateShader(type):
    try:
        nativefunc = glCreateShader._native
    except AttributeError:
        nativefunc = glCreateShader._native = _get_gl_func("glCreateShader", ctypes.c_uint, (ctypes.c_uint,))
    return nativefunc(type)


# void = glCullFace(GLenum mode)
def glCullFace(mode):
    try:
        nativefunc = glCullFace._native
    except AttributeError:
        nativefunc = glCullFace._native = _get_gl_func("glCullFace", None, (ctypes.c_uint,))
    nativefunc(mode)


# void = glDeleteBuffers(GLsizei n, GLuint* buffers)
def glDeleteBuffer(buffer):
    n = 1
    buffers = (ctypes.c_uint*n)(buffer)
    try:
        nativefunc = glDeleteBuffer._native
    except AttributeError:
        nativefunc = glDeleteBuffer._native = _get_gl_func("glDeleteBuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, buffers)


# void = glDeleteFramebuffers(GLsizei n, GLuint* framebuffers)
def glDeleteFramebuffer(framebuffer):
    n = 1
    framebuffers = (ctypes.c_uint*n)(framebuffer)
    try:
        nativefunc = glDeleteFramebuffer._native
    except AttributeError:
        nativefunc = glDeleteFramebuffer._native = _get_gl_func("glDeleteFramebuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, framebuffers)


# void = glDeleteProgram(GLuint program)
def glDeleteProgram(program):
    try:
        nativefunc = glDeleteProgram._native
    except AttributeError:
        nativefunc = glDeleteProgram._native = _get_gl_func("glDeleteProgram", None, (ctypes.c_uint,))
    nativefunc(program)


# void = glDeleteRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glDeleteRenderbuffer(renderbuffer):
    n = 1
    renderbuffers = (ctypes.c_uint*n)(renderbuffer)
    try:
        nativefunc = glDeleteRenderbuffer._native
    except AttributeError:
        nativefunc = glDeleteRenderbuffer._native = _get_gl_func("glDeleteRenderbuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, renderbuffers)


# void = glDeleteShader(GLuint shader)
def glDeleteShader(shader):
    try:
        nativefunc = glDeleteShader._native
    except AttributeError:
        nativefunc = glDeleteShader._native = _get_gl_func("glDeleteShader", None, (ctypes.c_uint,))
    nativefunc(shader)


# void = glDeleteTextures(GLsizei n, GLuint* textures)
def glDeleteTexture(texture):
    n = 1
    textures = (ctypes.c_uint*n)(texture)
    try:
        nativefunc = glDeleteTexture._native
    except AttributeError:
        nativefunc = glDeleteTexture._native = _get_gl_func("glDeleteTextures", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, textures)


# void = glDepthFunc(GLenum func)
def glDepthFunc(func):
    try:
        nativefunc = glDepthFunc._native
    except AttributeError:
        nativefunc = glDepthFunc._native = _get_gl_func("glDepthFunc", None, (ctypes.c_uint,))
    nativefunc(func)


# void = glDepthMask(GLboolean flag)
def glDepthMask(flag):
    try:
        nativefunc = glDepthMask._native
    except AttributeError:
        nativefunc = glDepthMask._native = _get_gl_func("glDepthMask", None, (ctypes.c_bool,))
    nativefunc(flag)


# void = glDepthRangef(GLclampf zNear, GLclampf zFar)
def glDepthRange(zNear, zFar):
    try:
        nativefunc = glDepthRange._native
    except AttributeError:
        nativefunc = glDepthRange._native = _get_gl_func("glDepthRange", None, (ctypes.c_double, ctypes.c_double,))
    nativefunc(zNear, zFar)


# void = glDetachShader(GLuint program, GLuint shader)
def glDetachShader(program, shader):
    try:
        nativefunc = glDetachShader._native
    except AttributeError:
        nativefunc = glDetachShader._native = _get_gl_func("glDetachShader", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(program, shader)


# void = glDisable(GLenum cap)
def glDisable(cap):
    try:
        nativefunc = glDisable._native
    except AttributeError:
        nativefunc = glDisable._native = _get_gl_func("glDisable", None, (ctypes.c_uint,))
    nativefunc(cap)


# void = glDisableVertexAttribArray(GLuint index)
def glDisableVertexAttribArray(index):
    try:
        nativefunc = glDisableVertexAttribArray._native
    except AttributeError:
        nativefunc = glDisableVertexAttribArray._native = _get_gl_func("glDisableVertexAttribArray", None, (ctypes.c_uint,))
    nativefunc(index)


# void = glDrawArrays(GLenum mode, GLint first, GLsizei count)
def glDrawArrays(mode, first, count):
    try:
        nativefunc = glDrawArrays._native
    except AttributeError:
        nativefunc = glDrawArrays._native = _get_gl_func("glDrawArrays", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int,))
    nativefunc(mode, first, count)


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
    try:
        nativefunc = glDrawElements._native
    except AttributeError:
        nativefunc = glDrawElements._native = _get_gl_func("glDrawElements", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p,))
    res = nativefunc(mode, count, type, indices)


# void = glEnable(GLenum cap)
def glEnable(cap):
    try:
        nativefunc = glEnable._native
    except AttributeError:
        nativefunc = glEnable._native = _get_gl_func("glEnable", None, (ctypes.c_uint,))
    nativefunc(cap)


# void = glEnableVertexAttribArray(GLuint index)
def glEnableVertexAttribArray(index):
    try:
        nativefunc = glEnableVertexAttribArray._native
    except AttributeError:
        nativefunc = glEnableVertexAttribArray._native = _get_gl_func("glEnableVertexAttribArray", None, (ctypes.c_uint,))
    nativefunc(index)


# void = glFinish()
def glFinish():
    try:
        nativefunc = glFinish._native
    except AttributeError:
        nativefunc = glFinish._native = _get_gl_func("glFinish", None, ())
    nativefunc()


# void = glFlush()
def glFlush():
    try:
        nativefunc = glFlush._native
    except AttributeError:
        nativefunc = glFlush._native = _get_gl_func("glFlush", None, ())
    nativefunc()


# void = glFramebufferRenderbuffer(GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer)
def glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer):
    try:
        nativefunc = glFramebufferRenderbuffer._native
    except AttributeError:
        nativefunc = glFramebufferRenderbuffer._native = _get_gl_func("glFramebufferRenderbuffer", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, attachment, renderbuffertarget, renderbuffer)


# void = glFramebufferTexture2D(GLenum target, GLenum attachment, GLenum textarget, GLuint texture, GLint level)
def glFramebufferTexture2D(target, attachment, textarget, texture, level):
    try:
        nativefunc = glFramebufferTexture2D._native
    except AttributeError:
        nativefunc = glFramebufferTexture2D._native = _get_gl_func("glFramebufferTexture2D", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_int,))
    nativefunc(target, attachment, textarget, texture, level)


# void = glFrontFace(GLenum mode)
def glFrontFace(mode):
    try:
        nativefunc = glFrontFace._native
    except AttributeError:
        nativefunc = glFrontFace._native = _get_gl_func("glFrontFace", None, (ctypes.c_uint,))
    nativefunc(mode)


# void = glGenBuffers(GLsizei n, GLuint* buffers)
def glCreateBuffer():
    n = 1
    buffers = (ctypes.c_uint*n)()
    try:
        nativefunc = glCreateBuffer._native
    except AttributeError:
        nativefunc = glCreateBuffer._native = _get_gl_func("glGenBuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, buffers)
    return buffers[0]


# void = glGenFramebuffers(GLsizei n, GLuint* framebuffers)
def glCreateFramebuffer():
    n = 1
    framebuffers = (ctypes.c_uint*n)()
    try:
        nativefunc = glCreateFramebuffer._native
    except AttributeError:
        nativefunc = glCreateFramebuffer._native = _get_gl_func("glGenFramebuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, framebuffers)
    return framebuffers[0]


# void = glGenRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glCreateRenderbuffer():
    n = 1
    renderbuffers = (ctypes.c_uint*n)()
    try:
        nativefunc = glCreateRenderbuffer._native
    except AttributeError:
        nativefunc = glCreateRenderbuffer._native = _get_gl_func("glGenRenderbuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, renderbuffers)
    return renderbuffers[0]


# void = glGenTextures(GLsizei n, GLuint* textures)
def glCreateTexture():
    n = 1
    textures = (ctypes.c_uint*n)()
    try:
        nativefunc = glCreateTexture._native
    except AttributeError:
        nativefunc = glCreateTexture._native = _get_gl_func("glGenTextures", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(n, textures)
    return textures[0]


# void = glGenerateMipmap(GLenum target)
def glGenerateMipmap(target):
    try:
        nativefunc = glGenerateMipmap._native
    except AttributeError:
        nativefunc = glGenerateMipmap._native = _get_gl_func("glGenerateMipmap", None, (ctypes.c_uint,))
    nativefunc(target)


# void = glGetActiveAttrib(GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name)
def glGetActiveAttrib(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    try:
        nativefunc = glGetActiveAttrib._native
    except AttributeError:
        nativefunc = glGetActiveAttrib._native = _get_gl_func("glGetActiveAttrib", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,))
    res = nativefunc(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


# void = glGetActiveUniform(GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name)
def glGetActiveUniform(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    try:
        nativefunc = glGetActiveUniform._native
    except AttributeError:
        nativefunc = glGetActiveUniform._native = _get_gl_func("glGetActiveUniform", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,))
    res = nativefunc(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


# void = glGetAttachedShaders(GLuint program, GLsizei maxcount, GLsizei* count, GLuint* shaders)
def glGetAttachedShaders(program):
    maxcount = 256
    count = (ctypes.c_int*1)()
    shaders = (ctypes.c_uint*maxcount)()
    try:
        nativefunc = glGetAttachedShaders._native
    except AttributeError:
        nativefunc = glGetAttachedShaders._native = _get_gl_func("glGetAttachedShaders", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint),))
    res = nativefunc(program, maxcount, count, shaders)
    return tuple(shaders[:count[0]])


# GLint = glGetAttribLocation(GLuint program, GLchar* name)
def glGetAttribLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        nativefunc = glGetAttribLocation._native
    except AttributeError:
        nativefunc = glGetAttribLocation._native = _get_gl_func("glGetAttribLocation", ctypes.c_int, (ctypes.c_uint, ctypes.c_char_p,))
    res = nativefunc(program, name)
    return res


# void = glGetBooleanv(GLenum pname, GLboolean* params)
def _glGetBooleanv(pname):
    params = (ctypes.c_bool*1)()
    try:
        nativefunc = _glGetBooleanv._native
    except AttributeError:
        nativefunc = _glGetBooleanv._native = _get_gl_func("glGetBooleanv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_bool),))
    res = nativefunc(pname, params)
    return params[0]


# void = glGetBufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetBufferParameter(target, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    try:
        nativefunc = glGetBufferParameter._native
    except AttributeError:
        nativefunc = glGetBufferParameter._native = _get_gl_func("glGetBufferParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(target, pname, params)
    return params[0]


# GLenum = glGetError()
def glGetError():
    try:
        nativefunc = glGetError._native
    except AttributeError:
        nativefunc = glGetError._native = _get_gl_func("glGetError", ctypes.c_uint, ())
    return nativefunc()


# void = glGetFloatv(GLenum pname, GLfloat* params)
def _glGetFloatv(pname):
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        nativefunc = _glGetFloatv._native
    except AttributeError:
        nativefunc = _glGetFloatv._native = _get_gl_func("glGetFloatv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = nativefunc(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


# void = glGetFramebufferAttachmentParameteriv(GLenum target, GLenum attachment, GLenum pname, GLint* params)
def glGetFramebufferAttachmentParameter(target, attachment, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    try:
        nativefunc = glGetFramebufferAttachmentParameter._native
    except AttributeError:
        nativefunc = glGetFramebufferAttachmentParameter._native = _get_gl_func("glGetFramebufferAttachmentParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(target, attachment, pname, params)
    return params[0]


# void = glGetIntegerv(GLenum pname, GLint* params)
def _glGetIntegerv(pname):
    n = 16
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*n)(*[d for i in range(n)])
    try:
        nativefunc = _glGetIntegerv._native
    except AttributeError:
        nativefunc = _glGetIntegerv._native = _get_gl_func("glGetIntegerv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


# void = glGetProgramInfoLog(GLuint program, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetProgramInfoLog(program):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    try:
        nativefunc = glGetProgramInfoLog._native
    except AttributeError:
        nativefunc = glGetProgramInfoLog._native = _get_gl_func("glGetProgramInfoLog", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = nativefunc(program, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


# void = glGetProgramiv(GLuint program, GLenum pname, GLint* params)
def glGetProgramParameter(program, pname):
    params = (ctypes.c_int*1)()
    try:
        nativefunc = glGetProgramParameter._native
    except AttributeError:
        nativefunc = glGetProgramParameter._native = _get_gl_func("glGetProgramiv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(program, pname, params)
    return params[0]


# void = glGetRenderbufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetRenderbufferParameter(target, pname):
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    try:
        nativefunc = glGetRenderbufferParameter._native
    except AttributeError:
        nativefunc = glGetRenderbufferParameter._native = _get_gl_func("glGetRenderbufferParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(target, pname, params)
    return params[0]


# void = glGetShaderInfoLog(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetShaderInfoLog(shader):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    try:
        nativefunc = glGetShaderInfoLog._native
    except AttributeError:
        nativefunc = glGetShaderInfoLog._native = _get_gl_func("glGetShaderInfoLog", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = nativefunc(shader, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


# void = glGetShaderPrecisionFormat(GLenum shadertype, GLenum precisiontype, GLint* range, GLint* precision)
def glGetShaderPrecisionFormat(shadertype, precisiontype):
    range = (ctypes.c_int*1)()
    precision = (ctypes.c_int*1)()
    try:
        nativefunc = glGetShaderPrecisionFormat._native
    except AttributeError:
        nativefunc = glGetShaderPrecisionFormat._native = _get_gl_func("glGetShaderPrecisionFormat", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(shadertype, precisiontype, range, precision)
    return range[0], precision[0]


# void = glGetShaderSource(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* source)
def glGetShaderSource(shader):
    bufsize = 1024*1024
    length = (ctypes.c_int*1)()
    source = (ctypes.c_char*bufsize)()
    try:
        nativefunc = glGetShaderSource._native
    except AttributeError:
        nativefunc = glGetShaderSource._native = _get_gl_func("glGetShaderSource", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = nativefunc(shader, bufsize, length, source)
    return source.value[:length[0]].decode('utf-8')


# void = glGetShaderiv(GLuint shader, GLenum pname, GLint* params)
def glGetShaderParameter(shader, pname):
    params = (ctypes.c_int*1)()
    try:
        nativefunc = glGetShaderParameter._native
    except AttributeError:
        nativefunc = glGetShaderParameter._native = _get_gl_func("glGetShaderiv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(shader, pname, params)
    return params[0]


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
    try:
        nativefunc = glGetParameter._native
    except AttributeError:
        nativefunc = glGetParameter._native = _get_gl_func("glGetString", ctypes.c_char_p, (ctypes.c_uint,))
    res = nativefunc(name)
    return ctypes.string_at(res).decode('utf-8') if res else ''


# void = glGetTexParameterfv(GLenum target, GLenum pname, GLfloat* params)
def glGetTexParameter(target, pname):
    d = float('Inf')
    params = (ctypes.c_float*1)(d)
    try:
        nativefunc = glGetTexParameter._native
    except AttributeError:
        nativefunc = glGetTexParameter._native = _get_gl_func("glGetTexParameterfv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = nativefunc(target, pname, params)
    return params[0]


# void = glGetUniformfv(GLuint program, GLint location, GLfloat* params)
def glGetUniform(program, location):
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        nativefunc = glGetUniform._native
    except AttributeError:
        nativefunc = glGetUniform._native = _get_gl_func("glGetUniformfv", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    res = nativefunc(program, location, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


# GLint = glGetUniformLocation(GLuint program, GLchar* name)
def glGetUniformLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        nativefunc = glGetUniformLocation._native
    except AttributeError:
        nativefunc = glGetUniformLocation._native = _get_gl_func("glGetUniformLocation", ctypes.c_int, (ctypes.c_uint, ctypes.c_char_p,))
    res = nativefunc(program, name)
    return res


# void = glGetVertexAttribfv(GLuint index, GLenum pname, GLfloat* params)
def glGetVertexAttrib(index, pname):
    n = 4
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        nativefunc = glGetVertexAttrib._native
    except AttributeError:
        nativefunc = glGetVertexAttrib._native = _get_gl_func("glGetVertexAttribfv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = nativefunc(index, pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


# void = glGetVertexAttribPointerv(GLuint index, GLenum pname, GLvoid** pointer)
def glGetVertexAttribOffset(index, pname):
    pointer = (ctypes.c_void_p*1)()
    try:
        nativefunc = glGetVertexAttribOffset._native
    except AttributeError:
        nativefunc = glGetVertexAttribOffset._native = _get_gl_func("glGetVertexAttribPointerv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p),))
    res = nativefunc(index, pname, pointer)
    return pointer[0] or 0


# void = glHint(GLenum target, GLenum mode)
def glHint(target, mode):
    try:
        nativefunc = glHint._native
    except AttributeError:
        nativefunc = glHint._native = _get_gl_func("glHint", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(target, mode)


# GLboolean = glIsBuffer(GLuint buffer)
def glIsBuffer(buffer):
    try:
        nativefunc = glIsBuffer._native
    except AttributeError:
        nativefunc = glIsBuffer._native = _get_gl_func("glIsBuffer", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(buffer)


# GLboolean = glIsEnabled(GLenum cap)
def glIsEnabled(cap):
    try:
        nativefunc = glIsEnabled._native
    except AttributeError:
        nativefunc = glIsEnabled._native = _get_gl_func("glIsEnabled", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(cap)


# GLboolean = glIsFramebuffer(GLuint framebuffer)
def glIsFramebuffer(framebuffer):
    try:
        nativefunc = glIsFramebuffer._native
    except AttributeError:
        nativefunc = glIsFramebuffer._native = _get_gl_func("glIsFramebuffer", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(framebuffer)


# GLboolean = glIsProgram(GLuint program)
def glIsProgram(program):
    try:
        nativefunc = glIsProgram._native
    except AttributeError:
        nativefunc = glIsProgram._native = _get_gl_func("glIsProgram", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(program)


# GLboolean = glIsRenderbuffer(GLuint renderbuffer)
def glIsRenderbuffer(renderbuffer):
    try:
        nativefunc = glIsRenderbuffer._native
    except AttributeError:
        nativefunc = glIsRenderbuffer._native = _get_gl_func("glIsRenderbuffer", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(renderbuffer)


# GLboolean = glIsShader(GLuint shader)
def glIsShader(shader):
    try:
        nativefunc = glIsShader._native
    except AttributeError:
        nativefunc = glIsShader._native = _get_gl_func("glIsShader", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(shader)


# GLboolean = glIsTexture(GLuint texture)
def glIsTexture(texture):
    try:
        nativefunc = glIsTexture._native
    except AttributeError:
        nativefunc = glIsTexture._native = _get_gl_func("glIsTexture", ctypes.c_bool, (ctypes.c_uint,))
    return nativefunc(texture)


# void = glLineWidth(GLfloat width)
def glLineWidth(width):
    try:
        nativefunc = glLineWidth._native
    except AttributeError:
        nativefunc = glLineWidth._native = _get_gl_func("glLineWidth", None, (ctypes.c_float,))
    nativefunc(width)


# void = glLinkProgram(GLuint program)
def glLinkProgram(program):
    try:
        nativefunc = glLinkProgram._native
    except AttributeError:
        nativefunc = glLinkProgram._native = _get_gl_func("glLinkProgram", None, (ctypes.c_uint,))
    nativefunc(program)


# void = glPixelStorei(GLenum pname, GLint param)
def glPixelStorei(pname, param):
    try:
        nativefunc = glPixelStorei._native
    except AttributeError:
        nativefunc = glPixelStorei._native = _get_gl_func("glPixelStorei", None, (ctypes.c_uint, ctypes.c_int,))
    nativefunc(pname, param)


# void = glPolygonOffset(GLfloat factor, GLfloat units)
def glPolygonOffset(factor, units):
    try:
        nativefunc = glPolygonOffset._native
    except AttributeError:
        nativefunc = glPolygonOffset._native = _get_gl_func("glPolygonOffset", None, (ctypes.c_float, ctypes.c_float,))
    nativefunc(factor, units)


# void = glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glReadPixels(x, y, width, height, format, type):
    # GL_ALPHA, GL_RGB, GL_RGBA, GL_DEPTH_COMPONENT
    t = {6406:1, 6407:3, 6408:4, 6402:1}[format]
    # GL_UNSIGNED_BYTE, GL_FLOAT
    nb = {5121:1, 5126:4}[type]
    size = int(width*height*t*nb)
    pixels = ctypes.create_string_buffer(size)
    try:
        nativefunc = glReadPixels._native
    except AttributeError:
        nativefunc = glReadPixels._native = _get_gl_func("glReadPixels", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = nativefunc(x, y, width, height, format, type, pixels)
    return pixels[:]


# void = glRenderbufferStorage(GLenum target, GLenum internalformat, GLsizei width, GLsizei height)
def glRenderbufferStorage(target, internalformat, width, height):
    try:
        nativefunc = glRenderbufferStorage._native
    except AttributeError:
        nativefunc = glRenderbufferStorage._native = _get_gl_func("glRenderbufferStorage", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_int,))
    nativefunc(target, internalformat, width, height)


# void = glSampleCoverage(GLclampf value, GLboolean invert)
def glSampleCoverage(value, invert):
    try:
        nativefunc = glSampleCoverage._native
    except AttributeError:
        nativefunc = glSampleCoverage._native = _get_gl_func("glSampleCoverage", None, (ctypes.c_float, ctypes.c_bool,))
    nativefunc(value, invert)


# void = glScissor(GLint x, GLint y, GLsizei width, GLsizei height)
def glScissor(x, y, width, height):
    try:
        nativefunc = glScissor._native
    except AttributeError:
        nativefunc = glScissor._native = _get_gl_func("glScissor", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(x, y, width, height)


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
    try:
        nativefunc = glShaderSource._native
    except AttributeError:
        nativefunc = glShaderSource._native = _get_gl_func("glShaderSource", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int),))
    res = nativefunc(shader, count, string, length)


# void = glStencilFunc(GLenum func, GLint ref, GLuint mask)
def glStencilFunc(func, ref, mask):
    try:
        nativefunc = glStencilFunc._native
    except AttributeError:
        nativefunc = glStencilFunc._native = _get_gl_func("glStencilFunc", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint,))
    nativefunc(func, ref, mask)


# void = glStencilFuncSeparate(GLenum face, GLenum func, GLint ref, GLuint mask)
def glStencilFuncSeparate(face, func, ref, mask):
    try:
        nativefunc = glStencilFuncSeparate._native
    except AttributeError:
        nativefunc = glStencilFuncSeparate._native = _get_gl_func("glStencilFuncSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint,))
    nativefunc(face, func, ref, mask)


# void = glStencilMask(GLuint mask)
def glStencilMask(mask):
    try:
        nativefunc = glStencilMask._native
    except AttributeError:
        nativefunc = glStencilMask._native = _get_gl_func("glStencilMask", None, (ctypes.c_uint,))
    nativefunc(mask)


# void = glStencilMaskSeparate(GLenum face, GLuint mask)
def glStencilMaskSeparate(face, mask):
    try:
        nativefunc = glStencilMaskSeparate._native
    except AttributeError:
        nativefunc = glStencilMaskSeparate._native = _get_gl_func("glStencilMaskSeparate", None, (ctypes.c_uint, ctypes.c_uint,))
    nativefunc(face, mask)


# void = glStencilOp(GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOp(fail, zfail, zpass):
    try:
        nativefunc = glStencilOp._native
    except AttributeError:
        nativefunc = glStencilOp._native = _get_gl_func("glStencilOp", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    nativefunc(fail, zfail, zpass)


# void = glStencilOpSeparate(GLenum face, GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOpSeparate(face, fail, zfail, zpass):
    try:
        nativefunc = glStencilOpSeparate._native
    except AttributeError:
        nativefunc = glStencilOpSeparate._native = _get_gl_func("glStencilOpSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    nativefunc(face, fail, zfail, zpass)


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
    try:
        nativefunc = glTexImage2D._native
    except AttributeError:
        nativefunc = glTexImage2D._native = _get_gl_func("glTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = nativefunc(target, level, internalformat, width, height, border, format, type, pixels)


def glTexParameterf(target, pname, param):
    try:
        nativefunc = glTexParameterf._native
    except AttributeError:
        nativefunc = glTexParameterf._native = _get_gl_func("glTexParameterf", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_float,))
    nativefunc(target, pname, param)
def glTexParameteri(target, pname, param):
    try:
        nativefunc = glTexParameteri._native
    except AttributeError:
        nativefunc = glTexParameteri._native = _get_gl_func("glTexParameteri", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int,))
    nativefunc(target, pname, param)


# void = glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    if not pixels.flags['C_CONTIGUOUS']:
        pixels = pixels.copy('C')
    pixels_ = pixels
    pixels = pixels_.ctypes.data
    height, width = pixels_.shape[:2]
    try:
        nativefunc = glTexSubImage2D._native
    except AttributeError:
        nativefunc = glTexSubImage2D._native = _get_gl_func("glTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = nativefunc(target, level, xoffset, yoffset, width, height, format, type, pixels)


def glUniform1f(location, v1):
    try:
        nativefunc = glUniform1f._native
    except AttributeError:
        nativefunc = glUniform1f._native = _get_gl_func("glUniform1f", None, (ctypes.c_int, ctypes.c_float,))
    nativefunc(location, v1)
def glUniform2f(location, v1, v2):
    try:
        nativefunc = glUniform2f._native
    except AttributeError:
        nativefunc = glUniform2f._native = _get_gl_func("glUniform2f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float,))
    nativefunc(location, v1, v2)
def glUniform3f(location, v1, v2, v3):
    try:
        nativefunc = glUniform3f._native
    except AttributeError:
        nativefunc = glUniform3f._native = _get_gl_func("glUniform3f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(location, v1, v2, v3)
def glUniform4f(location, v1, v2, v3, v4):
    try:
        nativefunc = glUniform4f._native
    except AttributeError:
        nativefunc = glUniform4f._native = _get_gl_func("glUniform4f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(location, v1, v2, v3, v4)
def glUniform1i(location, v1):
    try:
        nativefunc = glUniform1i._native
    except AttributeError:
        nativefunc = glUniform1i._native = _get_gl_func("glUniform1i", None, (ctypes.c_int, ctypes.c_int,))
    nativefunc(location, v1)
def glUniform2i(location, v1, v2):
    try:
        nativefunc = glUniform2i._native
    except AttributeError:
        nativefunc = glUniform2i._native = _get_gl_func("glUniform2i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(location, v1, v2)
def glUniform3i(location, v1, v2, v3):
    try:
        nativefunc = glUniform3i._native
    except AttributeError:
        nativefunc = glUniform3i._native = _get_gl_func("glUniform3i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(location, v1, v2, v3)
def glUniform4i(location, v1, v2, v3, v4):
    try:
        nativefunc = glUniform4i._native
    except AttributeError:
        nativefunc = glUniform4i._native = _get_gl_func("glUniform4i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(location, v1, v2, v3, v4)
def glUniform1fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        nativefunc = glUniform1fv._native
    except AttributeError:
        nativefunc = glUniform1fv._native = _get_gl_func("glUniform1fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, values)
def glUniform2fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        nativefunc = glUniform2fv._native
    except AttributeError:
        nativefunc = glUniform2fv._native = _get_gl_func("glUniform2fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, values)
def glUniform3fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        nativefunc = glUniform3fv._native
    except AttributeError:
        nativefunc = glUniform3fv._native = _get_gl_func("glUniform3fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, values)
def glUniform4fv(location, count, values):
    values = [float(val) for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        nativefunc = glUniform4fv._native
    except AttributeError:
        nativefunc = glUniform4fv._native = _get_gl_func("glUniform4fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, values)
def glUniform1iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        nativefunc = glUniform1iv._native
    except AttributeError:
        nativefunc = glUniform1iv._native = _get_gl_func("glUniform1iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    nativefunc(location, count, values)
def glUniform2iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        nativefunc = glUniform2iv._native
    except AttributeError:
        nativefunc = glUniform2iv._native = _get_gl_func("glUniform2iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    nativefunc(location, count, values)
def glUniform3iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        nativefunc = glUniform3iv._native
    except AttributeError:
        nativefunc = glUniform3iv._native = _get_gl_func("glUniform3iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    nativefunc(location, count, values)
def glUniform4iv(location, count, values):
    values = [int(val) for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        nativefunc = glUniform4iv._native
    except AttributeError:
        nativefunc = glUniform4iv._native = _get_gl_func("glUniform4iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    nativefunc(location, count, values)


def glUniformMatrix2fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    try:
        nativefunc = glUniformMatrix2fv._native
    except AttributeError:
        nativefunc = glUniformMatrix2fv._native = _get_gl_func("glUniformMatrix2fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, transpose, values)
def glUniformMatrix3fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    try:
        nativefunc = glUniformMatrix3fv._native
    except AttributeError:
        nativefunc = glUniformMatrix3fv._native = _get_gl_func("glUniformMatrix3fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, transpose, values)
def glUniformMatrix4fv(location, count, transpose, values):
    if not values.flags["C_CONTIGUOUS"]:
        values = values.copy()
    assert values.dtype.name == "float32"
    values_ = values
    values = values_.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    try:
        nativefunc = glUniformMatrix4fv._native
    except AttributeError:
        nativefunc = glUniformMatrix4fv._native = _get_gl_func("glUniformMatrix4fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    nativefunc(location, count, transpose, values)


# void = glUseProgram(GLuint program)
def glUseProgram(program):
    try:
        nativefunc = glUseProgram._native
    except AttributeError:
        nativefunc = glUseProgram._native = _get_gl_func("glUseProgram", None, (ctypes.c_uint,))
    nativefunc(program)


# void = glValidateProgram(GLuint program)
def glValidateProgram(program):
    try:
        nativefunc = glValidateProgram._native
    except AttributeError:
        nativefunc = glValidateProgram._native = _get_gl_func("glValidateProgram", None, (ctypes.c_uint,))
    nativefunc(program)


def glVertexAttrib1f(index, v1):
    try:
        nativefunc = glVertexAttrib1f._native
    except AttributeError:
        nativefunc = glVertexAttrib1f._native = _get_gl_func("glVertexAttrib1f", None, (ctypes.c_uint, ctypes.c_float,))
    nativefunc(index, v1)
def glVertexAttrib2f(index, v1, v2):
    try:
        nativefunc = glVertexAttrib2f._native
    except AttributeError:
        nativefunc = glVertexAttrib2f._native = _get_gl_func("glVertexAttrib2f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float,))
    nativefunc(index, v1, v2)
def glVertexAttrib3f(index, v1, v2, v3):
    try:
        nativefunc = glVertexAttrib3f._native
    except AttributeError:
        nativefunc = glVertexAttrib3f._native = _get_gl_func("glVertexAttrib3f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(index, v1, v2, v3)
def glVertexAttrib4f(index, v1, v2, v3, v4):
    try:
        nativefunc = glVertexAttrib4f._native
    except AttributeError:
        nativefunc = glVertexAttrib4f._native = _get_gl_func("glVertexAttrib4f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    nativefunc(index, v1, v2, v3, v4)


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
    try:
        nativefunc = glVertexAttribPointer._native
    except AttributeError:
        nativefunc = glVertexAttribPointer._native = _get_gl_func("glVertexAttribPointer", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p,))
    res = nativefunc(indx, size, type, normalized, stride, ptr)


# void = glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
def glViewport(x, y, width, height):
    try:
        nativefunc = glViewport._native
    except AttributeError:
        nativefunc = glViewport._native = _get_gl_func("glViewport", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    nativefunc(x, y, width, height)


