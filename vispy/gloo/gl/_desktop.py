"""

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Subset of desktop GL API compatible with GL ES 2.0

"""

import ctypes
from .desktop import _lib, _get_gl_func


# void = glActiveTexture(GLenum texture)
def glActiveTexture(texture):
    try:
        func = glActiveTexture._native
    except AttributeError:
        func = glActiveTexture._native = _get_gl_func("glActiveTexture", None, (ctypes.c_uint,))
    func(texture)


# void = glAttachShader(GLuint program, GLuint shader)
def glAttachShader(program, shader):
    try:
        func = glAttachShader._native
    except AttributeError:
        func = glAttachShader._native = _get_gl_func("glAttachShader", None, (ctypes.c_uint, ctypes.c_uint,))
    func(program, shader)


# void = glBindAttribLocation(GLuint program, GLuint index, GLchar* name)
def glBindAttribLocation(program, index, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        func = glBindAttribLocation._native
    except AttributeError:
        func = glBindAttribLocation._native = _get_gl_func("glBindAttribLocation", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p,))
    res = func(program, index, name)


# void = glBindBuffer(GLenum target, GLuint buffer)
def glBindBuffer(target, buffer):
    try:
        func = glBindBuffer._native
    except AttributeError:
        func = glBindBuffer._native = _get_gl_func("glBindBuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    func(target, buffer)


# void = glBindFramebuffer(GLenum target, GLuint framebuffer)
def glBindFramebuffer(target, framebuffer):
    try:
        func = glBindFramebuffer._native
    except AttributeError:
        func = glBindFramebuffer._native = _get_gl_func("glBindFramebuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    func(target, framebuffer)


# void = glBindRenderbuffer(GLenum target, GLuint renderbuffer)
def glBindRenderbuffer(target, renderbuffer):
    try:
        func = glBindRenderbuffer._native
    except AttributeError:
        func = glBindRenderbuffer._native = _get_gl_func("glBindRenderbuffer", None, (ctypes.c_uint, ctypes.c_uint,))
    func(target, renderbuffer)


# void = glBindTexture(GLenum target, GLuint texture)
def glBindTexture(target, texture):
    try:
        func = glBindTexture._native
    except AttributeError:
        func = glBindTexture._native = _get_gl_func("glBindTexture", None, (ctypes.c_uint, ctypes.c_uint,))
    func(target, texture)


# void = glBlendColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glBlendColor(red, green, blue, alpha):
    try:
        func = glBlendColor._native
    except AttributeError:
        func = glBlendColor._native = _get_gl_func("glBlendColor", None, (ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(red, green, blue, alpha)


# void = glBlendEquation(GLenum mode)
def glBlendEquation(mode):
    try:
        func = glBlendEquation._native
    except AttributeError:
        func = glBlendEquation._native = _get_gl_func("glBlendEquation", None, (ctypes.c_uint,))
    func(mode)


# void = glBlendEquationSeparate(GLenum modeRGB, GLenum modeAlpha)
def glBlendEquationSeparate(modeRGB, modeAlpha):
    try:
        func = glBlendEquationSeparate._native
    except AttributeError:
        func = glBlendEquationSeparate._native = _get_gl_func("glBlendEquationSeparate", None, (ctypes.c_uint, ctypes.c_uint,))
    func(modeRGB, modeAlpha)


# void = glBlendFunc(GLenum sfactor, GLenum dfactor)
def glBlendFunc(sfactor, dfactor):
    try:
        func = glBlendFunc._native
    except AttributeError:
        func = glBlendFunc._native = _get_gl_func("glBlendFunc", None, (ctypes.c_uint, ctypes.c_uint,))
    func(sfactor, dfactor)


# void = glBlendFuncSeparate(GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha, GLenum dstAlpha)
def glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha):
    try:
        func = glBlendFuncSeparate._native
    except AttributeError:
        func = glBlendFuncSeparate._native = _get_gl_func("glBlendFuncSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    func(srcRGB, dstRGB, srcAlpha, dstAlpha)


# void = glBufferData(GLenum target, GLsizeiptr size, GLvoid* data, GLenum usage)
def glBufferData(target, data, usage):
    """ Data can be numpy array or the size of data to allocate.
    """
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
        func = glBufferData._native
    except AttributeError:
        func = glBufferData._native = _get_gl_func("glBufferData", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint,))
    res = func(target, size, data, usage)


# void = glBufferSubData(GLenum target, GLintptr offset, GLsizeiptr size, GLvoid* data)
def glBufferSubData(target, offset, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.nbytes
    data = data_.ctypes.data
    try:
        func = glBufferSubData._native
    except AttributeError:
        func = glBufferSubData._native = _get_gl_func("glBufferSubData", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,))
    res = func(target, offset, size, data)


# GLenum = glCheckFramebufferStatus(GLenum target)
def glCheckFramebufferStatus(target):
    try:
        func = glCheckFramebufferStatus._native
    except AttributeError:
        func = glCheckFramebufferStatus._native = _get_gl_func("glCheckFramebufferStatus", ctypes.c_uint, (ctypes.c_uint,))
    return func(target)


# void = glClear(GLbitfield mask)
def glClear(mask):
    try:
        func = glClear._native
    except AttributeError:
        func = glClear._native = _get_gl_func("glClear", None, (ctypes.c_uint,))
    func(mask)


# void = glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
def glClearColor(red, green, blue, alpha):
    try:
        func = glClearColor._native
    except AttributeError:
        func = glClearColor._native = _get_gl_func("glClearColor", None, (ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(red, green, blue, alpha)


# void = glClearDepthf(GLclampf depth)
def glClearDepth(depth):
    try:
        func = glClearDepth._native
    except AttributeError:
        func = glClearDepth._native = _get_gl_func("glClearDepthf", None, (ctypes.c_float,))
    func(depth)


# void = glClearStencil(GLint s)
def glClearStencil(s):
    try:
        func = glClearStencil._native
    except AttributeError:
        func = glClearStencil._native = _get_gl_func("glClearStencil", None, (ctypes.c_int,))
    func(s)


# void = glColorMask(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
def glColorMask(red, green, blue, alpha):
    try:
        func = glColorMask._native
    except AttributeError:
        func = glColorMask._native = _get_gl_func("glColorMask", None, (ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool,))
    func(red, green, blue, alpha)


# void = glCompileShader(GLuint shader)
def glCompileShader(shader):
    try:
        func = glCompileShader._native
    except AttributeError:
        func = glCompileShader._native = _get_gl_func("glCompileShader", None, (ctypes.c_uint,))
    func(shader)


# void = glCompressedTexImage2D(GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize, GLvoid* data)
def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    # border = 0  # set in args
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    try:
        func = glCompressedTexImage2D._native
    except AttributeError:
        func = glCompressedTexImage2D._native = _get_gl_func("glCompressedTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,))
    res = func(target, level, internalformat, width, height, border, imageSize, data)


# void = glCompressedTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize, GLvoid* data)
def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    try:
        func = glCompressedTexSubImage2D._native
    except AttributeError:
        func = glCompressedTexSubImage2D._native = _get_gl_func("glCompressedTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p,))
    res = func(target, level, xoffset, yoffset, width, height, format, imageSize, data)


# void = glCopyTexImage2D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
def glCopyTexImage2D(target, level, internalformat, x, y, width, height, border):
    try:
        func = glCopyTexImage2D._native
    except AttributeError:
        func = glCopyTexImage2D._native = _get_gl_func("glCopyTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(target, level, internalformat, x, y, width, height, border)


# void = glCopyTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
def glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height):
    try:
        func = glCopyTexSubImage2D._native
    except AttributeError:
        func = glCopyTexSubImage2D._native = _get_gl_func("glCopyTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(target, level, xoffset, yoffset, x, y, width, height)


# GLuint = glCreateProgram()
def glCreateProgram():
    try:
        func = glCreateProgram._native
    except AttributeError:
        func = glCreateProgram._native = _get_gl_func("glCreateProgram", ctypes.c_uint, ())
    return func()


# GLuint = glCreateShader(GLenum type)
def glCreateShader(type):
    try:
        func = glCreateShader._native
    except AttributeError:
        func = glCreateShader._native = _get_gl_func("glCreateShader", ctypes.c_uint, (ctypes.c_uint,))
    return func(type)


# void = glCullFace(GLenum mode)
def glCullFace(mode):
    try:
        func = glCullFace._native
    except AttributeError:
        func = glCullFace._native = _get_gl_func("glCullFace", None, (ctypes.c_uint,))
    func(mode)


# void = glDeleteBuffers(GLsizei n, GLuint* buffers)
def glDeleteBuffer(buffer):
    n = 1
    buffers = (ctypes.c_uint*n)(buffer)
    try:
        func = glDeleteBuffer._native
    except AttributeError:
        func = glDeleteBuffer._native = _get_gl_func("glDeleteBuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, buffers)


# void = glDeleteFramebuffers(GLsizei n, GLuint* framebuffers)
def glDeleteFramebuffer(framebuffer):
    n = 1
    buffers = (ctypes.c_uint*n)(framebuffer)
    try:
        func = glDeleteFramebuffer._native
    except AttributeError:
        func = glDeleteFramebuffer._native = _get_gl_func("glDeleteFramebuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, framebuffers)


# void = glDeleteProgram(GLuint program)
def glDeleteProgram(program):
    try:
        func = glDeleteProgram._native
    except AttributeError:
        func = glDeleteProgram._native = _get_gl_func("glDeleteProgram", None, (ctypes.c_uint,))
    func(program)


# void = glDeleteRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glDeleteRenderbuffer(renderbuffer):
    n = 1
    buffers = (ctypes.c_uint*n)(renderbuffer)
    try:
        func = glDeleteRenderbuffer._native
    except AttributeError:
        func = glDeleteRenderbuffer._native = _get_gl_func("glDeleteRenderbuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, renderbuffers)


# void = glDeleteShader(GLuint shader)
def glDeleteShader(shader):
    try:
        func = glDeleteShader._native
    except AttributeError:
        func = glDeleteShader._native = _get_gl_func("glDeleteShader", None, (ctypes.c_uint,))
    func(shader)


# void = glDeleteTextures(GLsizei n, GLuint* textures)
def glDeleteTexture(texture):
    n = 1
    buffers = (ctypes.c_uint*n)(texture)
    try:
        func = glDeleteTexture._native
    except AttributeError:
        func = glDeleteTexture._native = _get_gl_func("glDeleteTextures", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, textures)


# void = glDepthFunc(GLenum func)
def glDepthFunc(func):
    try:
        func = glDepthFunc._native
    except AttributeError:
        func = glDepthFunc._native = _get_gl_func("glDepthFunc", None, (ctypes.c_uint,))
    func(func)


# void = glDepthMask(GLboolean flag)
def glDepthMask(flag):
    try:
        func = glDepthMask._native
    except AttributeError:
        func = glDepthMask._native = _get_gl_func("glDepthMask", None, (ctypes.c_bool,))
    func(flag)


# void = glDepthRangef(GLclampf zNear, GLclampf zFar)
def glDepthRange(zNear, zFar):
    try:
        func = glDepthRange._native
    except AttributeError:
        func = glDepthRange._native = _get_gl_func("glDepthRangef", None, (ctypes.c_float, ctypes.c_float,))
    func(zNear, zFar)


# void = glDetachShader(GLuint program, GLuint shader)
def glDetachShader(program, shader):
    try:
        func = glDetachShader._native
    except AttributeError:
        func = glDetachShader._native = _get_gl_func("glDetachShader", None, (ctypes.c_uint, ctypes.c_uint,))
    func(program, shader)


# void = glDisable(GLenum cap)
def glDisable(cap):
    try:
        func = glDisable._native
    except AttributeError:
        func = glDisable._native = _get_gl_func("glDisable", None, (ctypes.c_uint,))
    func(cap)


# void = glDisableVertexAttribArray(GLuint index)
def glDisableVertexAttribArray(index):
    try:
        func = glDisableVertexAttribArray._native
    except AttributeError:
        func = glDisableVertexAttribArray._native = _get_gl_func("glDisableVertexAttribArray", None, (ctypes.c_uint,))
    func(index)


# void = glDrawArrays(GLenum mode, GLint first, GLsizei count)
def glDrawArrays(mode, first, count):
    try:
        func = glDrawArrays._native
    except AttributeError:
        func = glDrawArrays._native = _get_gl_func("glDrawArrays", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int,))
    func(mode, first, count)


# void = glDrawElements(GLenum mode, GLsizei count, GLenum type, GLvoid* indices)
def glDrawElements(mode, count, type, offset):
    """ offset can be integer offset or array of indices.
    """
    if offset is None:
        offset = ctypes.c_void_p(0)
    elif isinstance(offset, c_void_p):
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
        func = glDrawElements._native
    except AttributeError:
        func = glDrawElements._native = _get_gl_func("glDrawElements", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p,))
    res = func(mode, count, type, indices)


# void = glEnable(GLenum cap)
def glEnable(cap):
    try:
        func = glEnable._native
    except AttributeError:
        func = glEnable._native = _get_gl_func("glEnable", None, (ctypes.c_uint,))
    func(cap)


# void = glEnableVertexAttribArray(GLuint index)
def glEnableVertexAttribArray(index):
    try:
        func = glEnableVertexAttribArray._native
    except AttributeError:
        func = glEnableVertexAttribArray._native = _get_gl_func("glEnableVertexAttribArray", None, (ctypes.c_uint,))
    func(index)


# void = glFinish()
def glFinish():
    try:
        func = glFinish._native
    except AttributeError:
        func = glFinish._native = _get_gl_func("glFinish", None, ())
    func()


# void = glFlush()
def glFlush():
    try:
        func = glFlush._native
    except AttributeError:
        func = glFlush._native = _get_gl_func("glFlush", None, ())
    func()


# void = glFramebufferRenderbuffer(GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer)
def glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer):
    try:
        func = glFramebufferRenderbuffer._native
    except AttributeError:
        func = glFramebufferRenderbuffer._native = _get_gl_func("glFramebufferRenderbuffer", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    func(target, attachment, renderbuffertarget, renderbuffer)


# void = glFramebufferTexture2D(GLenum target, GLenum attachment, GLenum textarget, GLuint texture, GLint level)
def glFramebufferTexture2D(target, attachment, textarget, texture, level):
    try:
        func = glFramebufferTexture2D._native
    except AttributeError:
        func = glFramebufferTexture2D._native = _get_gl_func("glFramebufferTexture2D", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_int,))
    func(target, attachment, textarget, texture, level)


# void = glFrontFace(GLenum mode)
def glFrontFace(mode):
    try:
        func = glFrontFace._native
    except AttributeError:
        func = glFrontFace._native = _get_gl_func("glFrontFace", None, (ctypes.c_uint,))
    func(mode)


# void = glGenBuffers(GLsizei n, GLuint* buffers)
def glCreateBuffer():
    n = 1
    buffers = (ctypes.c_uint*n)()
    try:
        func = glCreateBuffer._native
    except AttributeError:
        func = glCreateBuffer._native = _get_gl_func("glGenBuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, buffers)
    return buffers[0]


# void = glGenFramebuffers(GLsizei n, GLuint* framebuffers)
def glCreateFramebuffer():
    n = 1
    framebuffers = (ctypes.c_uint*n)()
    try:
        func = glCreateFramebuffer._native
    except AttributeError:
        func = glCreateFramebuffer._native = _get_gl_func("glGenFramebuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, framebuffers)
    return framebuffers[0]


# void = glGenRenderbuffers(GLsizei n, GLuint* renderbuffers)
def glCreateRenderbuffer():
    n = 1
    renderbuffers = (ctypes.c_uint*n)()
    try:
        func = glCreateRenderbuffer._native
    except AttributeError:
        func = glCreateRenderbuffer._native = _get_gl_func("glGenRenderbuffers", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, renderbuffers)
    return renderbuffers[0]


# void = glGenTextures(GLsizei n, GLuint* textures)
def glCreateTexture():
    n = 1
    textures = (ctypes.c_uint*n)()
    try:
        func = glCreateTexture._native
    except AttributeError:
        func = glCreateTexture._native = _get_gl_func("glGenTextures", None, (ctypes.c_int, ctypes.POINTER(ctypes.c_uint),))
    res = func(n, textures)
    return textures[0]


# void = glGenerateMipmap(GLenum target)
def glGenerateMipmap(target):
    try:
        func = glGenerateMipmap._native
    except AttributeError:
        func = glGenerateMipmap._native = _get_gl_func("glGenerateMipmap", None, (ctypes.c_uint,))
    func(target)


# void = glGetActiveAttrib(GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name)
def glGetActiveAttrib(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    try:
        func = glGetActiveAttrib._native
    except AttributeError:
        func = glGetActiveAttrib._native = _get_gl_func("glGetActiveAttrib", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,))
    res = func(program, index, bufsize, length, size, type, name)
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
        func = glGetActiveUniform._native
    except AttributeError:
        func = glGetActiveUniform._native = _get_gl_func("glGetActiveUniform", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,))
    res = func(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]


# void = glGetAttachedShaders(GLuint program, GLsizei maxcount, GLsizei* count, GLuint* shaders)
def glGetAttachedShaders(program):
    maxcount = 256
    count = (ctypes.c_int*1)()
    shaders = (ctypes.c_uint*maxcount)()
    try:
        func = glGetAttachedShaders._native
    except AttributeError:
        func = glGetAttachedShaders._native = _get_gl_func("glGetAttachedShaders", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint),))
    res = func(program, maxcount, count, shaders)
    return tuple(shaders[:count[0]])


# GLint = glGetAttribLocation(GLuint program, GLchar* name)
def glGetAttribLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        func = glGetAttribLocation._native
    except AttributeError:
        func = glGetAttribLocation._native = _get_gl_func("glGetAttribLocation", ctypes.c_int, (ctypes.c_uint, ctypes.c_char_p,))
    res = func(program, name)
    return res


# void = glGetBooleanv(GLenum pname, GLboolean* params)
def _glGetBooleanv(pname):
    params = (ctypes.c_bool*1)()
    try:
        func = _glGetBooleanv._native
    except AttributeError:
        func = _glGetBooleanv._native = _get_gl_func("glGetBooleanv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_bool),))
    res = func(pname, params)
    return params[0]


# void = glGetBufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetBufferParameter(target, pname):
    data = (ctypes.c_int*1)()
    try:
        func = glGetBufferParameter._native
    except AttributeError:
        func = glGetBufferParameter._native = _get_gl_func("glGetBufferParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(target, pname, params)
    return data[0]


# GLenum = glGetError()
def glGetError():
    try:
        func = glGetError._native
    except AttributeError:
        func = glGetError._native = _get_gl_func("glGetError", ctypes.c_uint, ())
    return func()


# void = glGetFloatv(GLenum pname, GLfloat* params)
def _glGetFloatv(pname):
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        func = _glGetFloatv._native
    except AttributeError:
        func = _glGetFloatv._native = _get_gl_func("glGetFloatv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = func(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return params


# void = glGetFramebufferAttachmentParameteriv(GLenum target, GLenum attachment, GLenum pname, GLint* params)
def glGetFramebufferAttachmentParameter(target, attachment, pname):
    params = (ctypes.c_int*1)()
    try:
        func = glGetFramebufferAttachmentParameter._native
    except AttributeError:
        func = glGetFramebufferAttachmentParameter._native = _get_gl_func("glGetFramebufferAttachmentParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(target, attachment, pname, params)
    return params[0]


# void = glGetIntegerv(GLenum pname, GLint* params)
def _glGetIntegerv(pname):
    n = 16
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*n)(*[d for i in range(n)])
    try:
        func = _glGetIntegerv._native
    except AttributeError:
        func = _glGetIntegerv._native = _get_gl_func("glGetIntegerv", None, (ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return params


# void = glGetProgramInfoLog(GLuint program, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetProgramInfoLog(program):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    try:
        func = glGetProgramInfoLog._native
    except AttributeError:
        func = glGetProgramInfoLog._native = _get_gl_func("glGetProgramInfoLog", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = func(program, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


# void = glGetProgramiv(GLuint program, GLenum pname, GLint* params)
def glGetProgramParameter(program, pname):
    params = (ctypes.c_int*1)()
    try:
        func = glGetProgramParameter._native
    except AttributeError:
        func = glGetProgramParameter._native = _get_gl_func("glGetProgramiv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(program, pname, params)
    return params[0]


# void = glGetRenderbufferParameteriv(GLenum target, GLenum pname, GLint* params)
def glGetRenderbufferParameter(target, pname):
    params = (ctypes.c_int*1)()
    try:
        func = glGetRenderbufferParameter._native
    except AttributeError:
        func = glGetRenderbufferParameter._native = _get_gl_func("glGetRenderbufferParameteriv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(target, pname, params)
    return params[0]


# void = glGetShaderInfoLog(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* infolog)
def glGetShaderInfoLog(shader):
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    try:
        func = glGetShaderInfoLog._native
    except AttributeError:
        func = glGetShaderInfoLog._native = _get_gl_func("glGetShaderInfoLog", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = func(shader, bufsize, length, infolog)
    return infolog[:length[0]].decode('utf-8')


# void = glGetShaderPrecisionFormat(GLenum shadertype, GLenum precisiontype, GLint* range, GLint* precision)
def glGetShaderPrecisionFormat(shadertype, precisiontype):
    range = (ctypes.c_int*1)()
    precision = (ctypes.c_int*1)()
    try:
        func = glGetShaderPrecisionFormat._native
    except AttributeError:
        func = glGetShaderPrecisionFormat._native = _get_gl_func("glGetShaderPrecisionFormat", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),))
    res = func(shadertype, precisiontype, range, precision)
    return range[0], precision[0]


# void = glGetShaderSource(GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* source)
def glGetShaderSource(shader):
    bufSize = 1024*1024
    length = (ctypes.c_int*1)()
    source = (ctypes.c_char*bufsize)()
    try:
        func = glGetShaderSource._native
    except AttributeError:
        func = glGetShaderSource._native = _get_gl_func("glGetShaderSource", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,))
    res = func(shader, bufsize, length, source)
    return source.value[:length[0]].decode('utf-8')


# void = glGetShaderiv(GLuint shader, GLenum pname, GLint* params)
def glGetShaderParameter(shader, pname):
    params = (ctypes.c_int*1)()
    try:
        func = glGetShaderParameter._native
    except AttributeError:
        func = glGetShaderParameter._native = _get_gl_func("glGetShaderiv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int),))
    res = func(shader, pname, params)
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
        func = glGetParameter._native
    except AttributeError:
        func = glGetParameter._native = _get_gl_func("glGetString", ctypes.c_char_p, (ctypes.c_uint,))
    res = func(name)
    return res.decode('utf-8')


# void = glGetTexParameterfv(GLenum target, GLenum pname, GLfloat* params)
def glGetTexParameter(target, pname):
    n = 1
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        func = glGetTexParameter._native
    except AttributeError:
        func = glGetTexParameter._native = _get_gl_func("glGetTexParameterfv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = func(target, pname, params)
    return params[0]


# void = glGetUniformfv(GLuint program, GLint location, GLfloat* params)
def glGetUniform(program, location):
    n = 16
    d = float('Inf')
    values = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        func = glGetUniform._native
    except AttributeError:
        func = glGetUniform._native = _get_gl_func("glGetUniformfv", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    res = func(program, location, params)
    values = [p for p in values if p!=d]
    if len(values) == 1:
        return values[0]
    else:
        return values


# GLint = glGetUniformLocation(GLuint program, GLchar* name)
def glGetUniformLocation(program, name):
    name = ctypes.c_char_p(name.encode('utf-8'))
    try:
        func = glGetUniformLocation._native
    except AttributeError:
        func = glGetUniformLocation._native = _get_gl_func("glGetUniformLocation", ctypes.c_int, (ctypes.c_uint, ctypes.c_char_p,))
    res = func(program, name)
    return res


# void = glGetVertexAttribfv(GLuint index, GLenum pname, GLfloat* params)
def glGetVertexAttrib(program, location):
    n = 4
    d = float('Inf')
    values = (ctypes.c_float*n)(*[d for i in range(n)])
    try:
        func = glGetVertexAttrib._native
    except AttributeError:
        func = glGetVertexAttrib._native = _get_gl_func("glGetVertexAttribfv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float),))
    res = func(index, pname, params)
    values = [p for p in values if p!=d]
    if len(values) == 1:
        return values[0]
    else:
        return values


# void = glGetVertexAttribPointerv(GLuint index, GLenum pname, GLvoid** pointer)
def glGetVertexAttribOffset(index, pname):
    pointer = (ctypes.c_void_p*1)()
    try:
        func = glGetVertexAttribOffset._native
    except AttributeError:
        func = glGetVertexAttribOffset._native = _get_gl_func("glGetVertexAttribPointerv", None, (ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p),))
    res = func(index, pname, pointer)
    return pointer[0]


# void = glHint(GLenum target, GLenum mode)
def glHint(target, mode):
    try:
        func = glHint._native
    except AttributeError:
        func = glHint._native = _get_gl_func("glHint", None, (ctypes.c_uint, ctypes.c_uint,))
    func(target, mode)


# GLboolean = glIsBuffer(GLuint buffer)
def glIsBuffer(buffer):
    try:
        func = glIsBuffer._native
    except AttributeError:
        func = glIsBuffer._native = _get_gl_func("glIsBuffer", ctypes.c_bool, (ctypes.c_uint,))
    return func(buffer)


# GLboolean = glIsEnabled(GLenum cap)
def glIsEnabled(cap):
    try:
        func = glIsEnabled._native
    except AttributeError:
        func = glIsEnabled._native = _get_gl_func("glIsEnabled", ctypes.c_bool, (ctypes.c_uint,))
    return func(cap)


# GLboolean = glIsFramebuffer(GLuint framebuffer)
def glIsFramebuffer(framebuffer):
    try:
        func = glIsFramebuffer._native
    except AttributeError:
        func = glIsFramebuffer._native = _get_gl_func("glIsFramebuffer", ctypes.c_bool, (ctypes.c_uint,))
    return func(framebuffer)


# GLboolean = glIsProgram(GLuint program)
def glIsProgram(program):
    try:
        func = glIsProgram._native
    except AttributeError:
        func = glIsProgram._native = _get_gl_func("glIsProgram", ctypes.c_bool, (ctypes.c_uint,))
    return func(program)


# GLboolean = glIsRenderbuffer(GLuint renderbuffer)
def glIsRenderbuffer(renderbuffer):
    try:
        func = glIsRenderbuffer._native
    except AttributeError:
        func = glIsRenderbuffer._native = _get_gl_func("glIsRenderbuffer", ctypes.c_bool, (ctypes.c_uint,))
    return func(renderbuffer)


# GLboolean = glIsShader(GLuint shader)
def glIsShader(shader):
    try:
        func = glIsShader._native
    except AttributeError:
        func = glIsShader._native = _get_gl_func("glIsShader", ctypes.c_bool, (ctypes.c_uint,))
    return func(shader)


# GLboolean = glIsTexture(GLuint texture)
def glIsTexture(texture):
    try:
        func = glIsTexture._native
    except AttributeError:
        func = glIsTexture._native = _get_gl_func("glIsTexture", ctypes.c_bool, (ctypes.c_uint,))
    return func(texture)


# void = glLineWidth(GLfloat width)
def glLineWidth(width):
    try:
        func = glLineWidth._native
    except AttributeError:
        func = glLineWidth._native = _get_gl_func("glLineWidth", None, (ctypes.c_float,))
    func(width)


# void = glLinkProgram(GLuint program)
def glLinkProgram(program):
    try:
        func = glLinkProgram._native
    except AttributeError:
        func = glLinkProgram._native = _get_gl_func("glLinkProgram", None, (ctypes.c_uint,))
    func(program)


# void = glPixelStorei(GLenum pname, GLint param)
def glPixelStorei(pname, param):
    try:
        func = glPixelStorei._native
    except AttributeError:
        func = glPixelStorei._native = _get_gl_func("glPixelStorei", None, (ctypes.c_uint, ctypes.c_int,))
    func(pname, param)


# void = glPolygonOffset(GLfloat factor, GLfloat units)
def glPolygonOffset(factor, units):
    try:
        func = glPolygonOffset._native
    except AttributeError:
        func = glPolygonOffset._native = _get_gl_func("glPolygonOffset", None, (ctypes.c_float, ctypes.c_float,))
    func(factor, units)


# void = glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glReadPixels(x, y, width, height, format, type):
    """ Return pixels as bytes.
    """
    # GL_ALPHA, GL_RGB, GL_RGBA
    t = {6406:1, 6407:3, 6408:4}[format]
    # we kind of only support type GL_UNSIGNED_BYTE
    size = int(width*height*t)
    pixels = (ctypes.c_uint8*size)()
    try:
        func = glReadPixels._native
    except AttributeError:
        func = glReadPixels._native = _get_gl_func("glReadPixels", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = func(x, y, width, height, format, type, pixels)
    return bytes(pixels)


# void = glRenderbufferStorage(GLenum target, GLenum internalformat, GLsizei width, GLsizei height)
def glRenderbufferStorage(target, internalformat, width, height):
    try:
        func = glRenderbufferStorage._native
    except AttributeError:
        func = glRenderbufferStorage._native = _get_gl_func("glRenderbufferStorage", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_int,))
    func(target, internalformat, width, height)


# void = glSampleCoverage(GLclampf value, GLboolean invert)
def glSampleCoverage(value, invert):
    try:
        func = glSampleCoverage._native
    except AttributeError:
        func = glSampleCoverage._native = _get_gl_func("glSampleCoverage", None, (ctypes.c_float, ctypes.c_bool,))
    func(value, invert)


# void = glScissor(GLint x, GLint y, GLsizei width, GLsizei height)
def glScissor(x, y, width, height):
    try:
        func = glScissor._native
    except AttributeError:
        func = glScissor._native = _get_gl_func("glScissor", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(x, y, width, height)


# void = glShaderSource(GLuint shader, GLsizei count, GLchar** string, GLint* length)
def glShaderSource(shader, source):
    if isinstance(source, (tuple, list)):
        strings = [s for s in source]
    else:
        strings = [source]
    count = len(strings)
    string = (ctypes.c_char_p*count)(*[s.encode('utf-8') for s in strings])
    length = (ctypes.c_int*count)(*[len(s) for s in strings])
    try:
        func = glShaderSource._native
    except AttributeError:
        func = glShaderSource._native = _get_gl_func("glShaderSource", None, (ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int),))
    res = func(shader, count, string, length)


# void = glStencilFunc(GLenum func, GLint ref, GLuint mask)
def glStencilFunc(func, ref, mask):
    try:
        func = glStencilFunc._native
    except AttributeError:
        func = glStencilFunc._native = _get_gl_func("glStencilFunc", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint,))
    func(func, ref, mask)


# void = glStencilFuncSeparate(GLenum face, GLenum func, GLint ref, GLuint mask)
def glStencilFuncSeparate(face, func, ref, mask):
    try:
        func = glStencilFuncSeparate._native
    except AttributeError:
        func = glStencilFuncSeparate._native = _get_gl_func("glStencilFuncSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint,))
    func(face, func, ref, mask)


# void = glStencilMask(GLuint mask)
def glStencilMask(mask):
    try:
        func = glStencilMask._native
    except AttributeError:
        func = glStencilMask._native = _get_gl_func("glStencilMask", None, (ctypes.c_uint,))
    func(mask)


# void = glStencilMaskSeparate(GLenum face, GLuint mask)
def glStencilMaskSeparate(face, mask):
    try:
        func = glStencilMaskSeparate._native
    except AttributeError:
        func = glStencilMaskSeparate._native = _get_gl_func("glStencilMaskSeparate", None, (ctypes.c_uint, ctypes.c_uint,))
    func(face, mask)


# void = glStencilOp(GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOp(fail, zfail, zpass):
    try:
        func = glStencilOp._native
    except AttributeError:
        func = glStencilOp._native = _get_gl_func("glStencilOp", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    func(fail, zfail, zpass)


# void = glStencilOpSeparate(GLenum face, GLenum fail, GLenum zfail, GLenum zpass)
def glStencilOpSeparate(face, fail, zfail, zpass):
    try:
        func = glStencilOpSeparate._native
    except AttributeError:
        func = glStencilOpSeparate._native = _get_gl_func("glStencilOpSeparate", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,))
    func(face, fail, zfail, zpass)


# void = glTexImage2D(GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid* pixels)
def glTexImage2D(target, level, internalformat, format, type, pixels):
    border = 0
    if isinstance(pixels, (tuple, list)):
        width, height = pixels
        pixels = ctypes.c_void_p(0)
        pixels = None
    else:
        if not pixels.flags['C_CONTIGUOUS']:
            pixels = pixels.copy('C')
        pixels_ = pixels
        pixels = pixels_.ctypes.data
        width, height = pixels_.shape[:2]
    try:
        func = glTexImage2D._native
    except AttributeError:
        func = glTexImage2D._native = _get_gl_func("glTexImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = func(target, level, internalformat, width, height, border, format, type, pixels)


def glTexParameterf(target, pname, param):
    try:
        func = glTexParameterf._native
    except AttributeError:
        func = glTexParameterf._native = _get_gl_func("glTexParameterf", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_float,))
    func(target, pname, param)
def glTexParameteri(target, pname, param):
    try:
        func = glTexParameteri._native
    except AttributeError:
        func = glTexParameteri._native = _get_gl_func("glTexParameteri", None, (ctypes.c_uint, ctypes.c_uint, ctypes.c_int,))
    func(target, pname, param)


# void = glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    if not pixels.flags['C_CONTIGUOUS']:
        pixels = pixels.copy('C')
    pixels_ = pixels
    pixels = pixels_.ctypes.data
    width, height = pixels_.shape[:2]
    try:
        func = glTexSubImage2D._native
    except AttributeError:
        func = glTexSubImage2D._native = _get_gl_func("glTexSubImage2D", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,))
    res = func(target, level, xoffset, yoffset, width, height, format, type, pixels)


def glUniform1f(location, v1):
    try:
        func = glUniform1f._native
    except AttributeError:
        func = glUniform1f._native = _get_gl_func("glUniform1f", None, (ctypes.c_int, ctypes.c_float,))
    func(location, v1)
def glUniform2f(location, v1, v2):
    try:
        func = glUniform2f._native
    except AttributeError:
        func = glUniform2f._native = _get_gl_func("glUniform2f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float,))
    func(location, v1, v2)
def glUniform3f(location, v1, v2, v3):
    try:
        func = glUniform3f._native
    except AttributeError:
        func = glUniform3f._native = _get_gl_func("glUniform3f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(location, v1, v2, v3)
def glUniform4f(location, v1, v2, v3, v4):
    try:
        func = glUniform4f._native
    except AttributeError:
        func = glUniform4f._native = _get_gl_func("glUniform4f", None, (ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(location, v1, v2, v3, v4)
def glUniform1i(location, v1):
    try:
        func = glUniform1i._native
    except AttributeError:
        func = glUniform1i._native = _get_gl_func("glUniform1i", None, (ctypes.c_int, ctypes.c_int,))
    func(location, v1)
def glUniform2i(location, v1, v2):
    try:
        func = glUniform2i._native
    except AttributeError:
        func = glUniform2i._native = _get_gl_func("glUniform2i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(location, v1, v2)
def glUniform3i(location, v1, v2, v3):
    try:
        func = glUniform3i._native
    except AttributeError:
        func = glUniform3i._native = _get_gl_func("glUniform3i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(location, v1, v2, v3)
def glUniform4i(location, v1, v2, v3, v4):
    try:
        func = glUniform4i._native
    except AttributeError:
        func = glUniform4i._native = _get_gl_func("glUniform4i", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(location, v1, v2, v3, v4)
def glUniform1fv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniform1fv._native
    except AttributeError:
        func = glUniform1fv._native = _get_gl_func("glUniform1fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    func(location, count, values)
def glUniform2fv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniform2fv._native
    except AttributeError:
        func = glUniform2fv._native = _get_gl_func("glUniform2fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    func(location, count, values)
def glUniform3fv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniform3fv._native
    except AttributeError:
        func = glUniform3fv._native = _get_gl_func("glUniform3fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    func(location, count, values)
def glUniform4fv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniform4fv._native
    except AttributeError:
        func = glUniform4fv._native = _get_gl_func("glUniform4fv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),))
    func(location, count, values)
def glUniform1iv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        func = glUniform1iv._native
    except AttributeError:
        func = glUniform1iv._native = _get_gl_func("glUniform1iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    func(location, count, values)
def glUniform2iv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        func = glUniform2iv._native
    except AttributeError:
        func = glUniform2iv._native = _get_gl_func("glUniform2iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    func(location, count, values)
def glUniform3iv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        func = glUniform3iv._native
    except AttributeError:
        func = glUniform3iv._native = _get_gl_func("glUniform3iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    func(location, count, values)
def glUniform4iv(location, count, values):
    values = [val for val in values]
    values = (ctypes.c_int*len(values))(*values)
    try:
        func = glUniform4iv._native
    except AttributeError:
        func = glUniform4iv._native = _get_gl_func("glUniform4iv", None, (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),))
    func(location, count, values)


def glUniformMatrix2fv(location, count, transpose, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniformMatrix2fv._native
    except AttributeError:
        func = glUniformMatrix2fv._native = _get_gl_func("glUniformMatrix2fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    func(location, count, transpose, values)
def glUniformMatrix3fv(location, count, transpose, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniformMatrix3fv._native
    except AttributeError:
        func = glUniformMatrix3fv._native = _get_gl_func("glUniformMatrix3fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    func(location, count, transpose, values)
def glUniformMatrix4fv(location, count, transpose, values):
    values = [val for val in values]
    values = (ctypes.c_float*len(values))(*values)
    try:
        func = glUniformMatrix4fv._native
    except AttributeError:
        func = glUniformMatrix4fv._native = _get_gl_func("glUniformMatrix4fv", None, (ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_float),))
    func(location, count, transpose, values)


# void = glUseProgram(GLuint program)
def glUseProgram(program):
    try:
        func = glUseProgram._native
    except AttributeError:
        func = glUseProgram._native = _get_gl_func("glUseProgram", None, (ctypes.c_uint,))
    func(program)


# void = glValidateProgram(GLuint program)
def glValidateProgram(program):
    try:
        func = glValidateProgram._native
    except AttributeError:
        func = glValidateProgram._native = _get_gl_func("glValidateProgram", None, (ctypes.c_uint,))
    func(program)


def glVertexAttrib1f(index, v1):
    try:
        func = glVertexAttrib1f._native
    except AttributeError:
        func = glVertexAttrib1f._native = _get_gl_func("glVertexAttrib1f", None, (ctypes.c_uint, ctypes.c_float,))
    func(index, v1)
def glVertexAttrib2f(index, v1, v2):
    try:
        func = glVertexAttrib2f._native
    except AttributeError:
        func = glVertexAttrib2f._native = _get_gl_func("glVertexAttrib2f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float,))
    func(index, v1, v2)
def glVertexAttrib3f(index, v1, v2, v3):
    try:
        func = glVertexAttrib3f._native
    except AttributeError:
        func = glVertexAttrib3f._native = _get_gl_func("glVertexAttrib3f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(index, v1, v2, v3)
def glVertexAttrib4f(index, v1, v2, v3, v4):
    try:
        func = glVertexAttrib4f._native
    except AttributeError:
        func = glVertexAttrib4f._native = _get_gl_func("glVertexAttrib4f", None, (ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,))
    func(index, v1, v2, v3, v4)


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
    ptr = offset
    try:
        func = glVertexAttribPointer._native
    except AttributeError:
        func = glVertexAttribPointer._native = _get_gl_func("glVertexAttribPointer", None, (ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p,))
    res = func(indx, size, type, normalized, stride, ptr)


# void = glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
def glViewport(x, y, width, height):
    try:
        func = glViewport._native
    except AttributeError:
        func = glViewport._native = _get_gl_func("glViewport", None, (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,))
    func(x, y, width, height)


