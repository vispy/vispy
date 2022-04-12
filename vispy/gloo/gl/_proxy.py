"""GL definitions converted to Python by codegen/createglapi.py.

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Base proxy API for GL ES 2.0.

"""

class BaseGLProxy(object):
    """ Base proxy class for the GL ES 2.0 API. Subclasses should
    implement __call__ to process the API calls.
    """
   
    def __call__(self, funcname, returns, *args):
        raise NotImplementedError()


    def glActiveTexture(self, texture):
        self("glActiveTexture", False, texture)


    def glAttachShader(self, program, shader):
        self("glAttachShader", False, program, shader)


    def glBindAttribLocation(self, program, index, name):
        self("glBindAttribLocation", False, program, index, name)


    def glBindBuffer(self, target, buffer):
        self("glBindBuffer", False, target, buffer)


    def glBindFramebuffer(self, target, framebuffer):
        self("glBindFramebuffer", False, target, framebuffer)


    def glBindRenderbuffer(self, target, renderbuffer):
        self("glBindRenderbuffer", False, target, renderbuffer)


    def glBindTexture(self, target, texture):
        self("glBindTexture", False, target, texture)


    def glBlendColor(self, red, green, blue, alpha):
        self("glBlendColor", False, red, green, blue, alpha)


    def glBlendEquation(self, mode):
        self("glBlendEquation", False, mode)


    def glBlendEquationSeparate(self, modeRGB, modeAlpha):
        self("glBlendEquationSeparate", False, modeRGB, modeAlpha)


    def glBlendFunc(self, sfactor, dfactor):
        self("glBlendFunc", False, sfactor, dfactor)


    def glBlendFuncSeparate(self, srcRGB, dstRGB, srcAlpha, dstAlpha):
        self("glBlendFuncSeparate", False, srcRGB, dstRGB, srcAlpha, dstAlpha)


    def glBufferData(self, target, data, usage):
        self("glBufferData", False, target, data, usage)


    def glBufferSubData(self, target, offset, data):
        self("glBufferSubData", False, target, offset, data)


    def glCheckFramebufferStatus(self, target):
        return self("glCheckFramebufferStatus", True, target)


    def glClear(self, mask):
        self("glClear", False, mask)


    def glClearColor(self, red, green, blue, alpha):
        self("glClearColor", False, red, green, blue, alpha)


    def glClearDepth(self, depth):
        self("glClearDepth", False, depth)


    def glClearStencil(self, s):
        self("glClearStencil", False, s)


    def glColorMask(self, red, green, blue, alpha):
        self("glColorMask", False, red, green, blue, alpha)


    def glCompileShader(self, shader):
        self("glCompileShader", False, shader)


    def glCompressedTexImage2D(self, target, level, internalformat, width, height, border, data):
        self("glCompressedTexImage2D", False, target, level, internalformat, width, height, border, data)


    def glCompressedTexSubImage2D(self, target, level, xoffset, yoffset, width, height, format, data):
        self("glCompressedTexSubImage2D", False, target, level, xoffset, yoffset, width, height, format, data)


    def glCopyTexImage2D(self, target, level, internalformat, x, y, width, height, border):
        self("glCopyTexImage2D", False, target, level, internalformat, x, y, width, height, border)


    def glCopyTexSubImage2D(self, target, level, xoffset, yoffset, x, y, width, height):
        self("glCopyTexSubImage2D", False, target, level, xoffset, yoffset, x, y, width, height)


    def glCreateProgram(self, ):
        return self("glCreateProgram", True, )


    def glCreateShader(self, type):
        return self("glCreateShader", True, type)


    def glCullFace(self, mode):
        self("glCullFace", False, mode)


    def glDeleteBuffer(self, buffer):
        self("glDeleteBuffer", False, buffer)


    def glDeleteFramebuffer(self, framebuffer):
        self("glDeleteFramebuffer", False, framebuffer)


    def glDeleteProgram(self, program):
        self("glDeleteProgram", False, program)


    def glDeleteRenderbuffer(self, renderbuffer):
        self("glDeleteRenderbuffer", False, renderbuffer)


    def glDeleteShader(self, shader):
        self("glDeleteShader", False, shader)


    def glDeleteTexture(self, texture):
        self("glDeleteTexture", False, texture)


    def glDepthFunc(self, func):
        self("glDepthFunc", False, func)


    def glDepthMask(self, flag):
        self("glDepthMask", False, flag)


    def glDepthRange(self, zNear, zFar):
        self("glDepthRange", False, zNear, zFar)


    def glDetachShader(self, program, shader):
        self("glDetachShader", False, program, shader)


    def glDisable(self, cap):
        self("glDisable", False, cap)


    def glDisableVertexAttribArray(self, index):
        self("glDisableVertexAttribArray", False, index)


    def glDrawArrays(self, mode, first, count):
        self("glDrawArrays", False, mode, first, count)


    def glDrawElements(self, mode, count, type, offset):
        self("glDrawElements", False, mode, count, type, offset)


    def glEnable(self, cap):
        self("glEnable", False, cap)


    def glEnableVertexAttribArray(self, index):
        self("glEnableVertexAttribArray", False, index)


    def glFinish(self, ):
        self("glFinish", False, )


    def glFlush(self, ):
        self("glFlush", False, )


    def glFramebufferRenderbuffer(self, target, attachment, renderbuffertarget, renderbuffer):
        self("glFramebufferRenderbuffer", False, target, attachment, renderbuffertarget, renderbuffer)


    def glFramebufferTexture2D(self, target, attachment, textarget, texture, level):
        self("glFramebufferTexture2D", False, target, attachment, textarget, texture, level)


    def glFrontFace(self, mode):
        self("glFrontFace", False, mode)


    def glCreateBuffer(self, ):
        return self("glCreateBuffer", True, )


    def glCreateFramebuffer(self, ):
        return self("glCreateFramebuffer", True, )


    def glCreateRenderbuffer(self, ):
        return self("glCreateRenderbuffer", True, )


    def glCreateTexture(self, ):
        return self("glCreateTexture", True, )


    def glGenerateMipmap(self, target):
        self("glGenerateMipmap", False, target)


    def glGetActiveAttrib(self, program, index):
        return self("glGetActiveAttrib", True, program, index)


    def glGetActiveUniform(self, program, index):
        return self("glGetActiveUniform", True, program, index)


    def glGetAttachedShaders(self, program):
        return self("glGetAttachedShaders", True, program)


    def glGetAttribLocation(self, program, name):
        return self("glGetAttribLocation", True, program, name)


    def _glGetBooleanv(self, pname):
        self("_glGetBooleanv", False, pname)


    def glGetBufferParameter(self, target, pname):
        return self("glGetBufferParameter", True, target, pname)


    def glGetError(self, ):
        return self("glGetError", True, )


    def _glGetFloatv(self, pname):
        self("_glGetFloatv", False, pname)


    def glGetFramebufferAttachmentParameter(self, target, attachment, pname):
        return self("glGetFramebufferAttachmentParameter", True, target, attachment, pname)


    def _glGetIntegerv(self, pname):
        self("_glGetIntegerv", False, pname)


    def glGetProgramInfoLog(self, program):
        return self("glGetProgramInfoLog", True, program)


    def glGetProgramParameter(self, program, pname):
        return self("glGetProgramParameter", True, program, pname)


    def glGetRenderbufferParameter(self, target, pname):
        return self("glGetRenderbufferParameter", True, target, pname)


    def glGetShaderInfoLog(self, shader):
        return self("glGetShaderInfoLog", True, shader)


    def glGetShaderPrecisionFormat(self, shadertype, precisiontype):
        return self("glGetShaderPrecisionFormat", True, shadertype, precisiontype)


    def glGetShaderSource(self, shader):
        return self("glGetShaderSource", True, shader)


    def glGetShaderParameter(self, shader, pname):
        return self("glGetShaderParameter", True, shader, pname)


    def glGetParameter(self, pname):
        return self("glGetParameter", True, pname)


    def glGetTexParameter(self, target, pname):
        return self("glGetTexParameter", True, target, pname)


    def glGetUniform(self, program, location):
        return self("glGetUniform", True, program, location)


    def glGetUniformLocation(self, program, name):
        return self("glGetUniformLocation", True, program, name)


    def glGetVertexAttrib(self, index, pname):
        return self("glGetVertexAttrib", True, index, pname)


    def glGetVertexAttribOffset(self, index, pname):
        return self("glGetVertexAttribOffset", True, index, pname)


    def glHint(self, target, mode):
        self("glHint", False, target, mode)


    def glIsBuffer(self, buffer):
        return self("glIsBuffer", True, buffer)


    def glIsEnabled(self, cap):
        return self("glIsEnabled", True, cap)


    def glIsFramebuffer(self, framebuffer):
        return self("glIsFramebuffer", True, framebuffer)


    def glIsProgram(self, program):
        return self("glIsProgram", True, program)


    def glIsRenderbuffer(self, renderbuffer):
        return self("glIsRenderbuffer", True, renderbuffer)


    def glIsShader(self, shader):
        return self("glIsShader", True, shader)


    def glIsTexture(self, texture):
        return self("glIsTexture", True, texture)


    def glLineWidth(self, width):
        self("glLineWidth", False, width)


    def glLinkProgram(self, program):
        self("glLinkProgram", False, program)


    def glPixelStorei(self, pname, param):
        self("glPixelStorei", False, pname, param)


    def glPolygonOffset(self, factor, units):
        self("glPolygonOffset", False, factor, units)


    def glReadPixels(self, x, y, width, height, format, type):
        return self("glReadPixels", True, x, y, width, height, format, type)


    def glRenderbufferStorage(self, target, internalformat, width, height):
        self("glRenderbufferStorage", False, target, internalformat, width, height)


    def glSampleCoverage(self, value, invert):
        self("glSampleCoverage", False, value, invert)


    def glScissor(self, x, y, width, height):
        self("glScissor", False, x, y, width, height)


    def glShaderSource(self, shader, source):
        self("glShaderSource", False, shader, source)


    def glStencilFunc(self, func, ref, mask):
        self("glStencilFunc", False, func, ref, mask)


    def glStencilFuncSeparate(self, face, func, ref, mask):
        self("glStencilFuncSeparate", False, face, func, ref, mask)


    def glStencilMask(self, mask):
        self("glStencilMask", False, mask)


    def glStencilMaskSeparate(self, face, mask):
        self("glStencilMaskSeparate", False, face, mask)


    def glStencilOp(self, fail, zfail, zpass):
        self("glStencilOp", False, fail, zfail, zpass)


    def glStencilOpSeparate(self, face, fail, zfail, zpass):
        self("glStencilOpSeparate", False, face, fail, zfail, zpass)


    def glTexImage2D(self, target, level, internalformat, format, type, pixels):
        self("glTexImage2D", False, target, level, internalformat, format, type, pixels)


    def glTexParameterf(self, target, pname, param):
        self("glTexParameterf", False, target, pname, param)
    def glTexParameteri(self, target, pname, param):
        self("glTexParameteri", False, target, pname, param)


    def glTexSubImage2D(self, target, level, xoffset, yoffset, format, type, pixels):
        self("glTexSubImage2D", False, target, level, xoffset, yoffset, format, type, pixels)


    def glUniform1f(self, location, v1):
        self("glUniform1f", False, location, v1)
    def glUniform2f(self, location, v1, v2):
        self("glUniform2f", False, location, v1, v2)
    def glUniform3f(self, location, v1, v2, v3):
        self("glUniform3f", False, location, v1, v2, v3)
    def glUniform4f(self, location, v1, v2, v3, v4):
        self("glUniform4f", False, location, v1, v2, v3, v4)
    def glUniform1i(self, location, v1):
        self("glUniform1i", False, location, v1)
    def glUniform2i(self, location, v1, v2):
        self("glUniform2i", False, location, v1, v2)
    def glUniform3i(self, location, v1, v2, v3):
        self("glUniform3i", False, location, v1, v2, v3)
    def glUniform4i(self, location, v1, v2, v3, v4):
        self("glUniform4i", False, location, v1, v2, v3, v4)
    def glUniform1fv(self, location, count, values):
        self("glUniform1fv", False, location, count, values)
    def glUniform2fv(self, location, count, values):
        self("glUniform2fv", False, location, count, values)
    def glUniform3fv(self, location, count, values):
        self("glUniform3fv", False, location, count, values)
    def glUniform4fv(self, location, count, values):
        self("glUniform4fv", False, location, count, values)
    def glUniform1iv(self, location, count, values):
        self("glUniform1iv", False, location, count, values)
    def glUniform2iv(self, location, count, values):
        self("glUniform2iv", False, location, count, values)
    def glUniform3iv(self, location, count, values):
        self("glUniform3iv", False, location, count, values)
    def glUniform4iv(self, location, count, values):
        self("glUniform4iv", False, location, count, values)


    def glUniformMatrix2fv(self, location, count, transpose, values):
        self("glUniformMatrix2fv", False, location, count, transpose, values)
    def glUniformMatrix3fv(self, location, count, transpose, values):
        self("glUniformMatrix3fv", False, location, count, transpose, values)
    def glUniformMatrix4fv(self, location, count, transpose, values):
        self("glUniformMatrix4fv", False, location, count, transpose, values)


    def glUseProgram(self, program):
        self("glUseProgram", False, program)


    def glValidateProgram(self, program):
        self("glValidateProgram", False, program)


    def glVertexAttrib1f(self, index, v1):
        self("glVertexAttrib1f", False, index, v1)
    def glVertexAttrib2f(self, index, v1, v2):
        self("glVertexAttrib2f", False, index, v1, v2)
    def glVertexAttrib3f(self, index, v1, v2, v3):
        self("glVertexAttrib3f", False, index, v1, v2, v3)
    def glVertexAttrib4f(self, index, v1, v2, v3, v4):
        self("glVertexAttrib4f", False, index, v1, v2, v3, v4)


    def glVertexAttribPointer(self, indx, size, type, normalized, stride, offset):
        self("glVertexAttribPointer", False, indx, size, type, normalized, stride, offset)


    def glViewport(self, x, y, width, height):
        self("glViewport", False, x, y, width, height)


