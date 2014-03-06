"""

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

Main proxy API for GL ES 2.0.

"""

def glShaderSource_compat(handle, code):
    return PROXY["glShaderSource_compat"](handle, code)


def glActiveTexture(texture):
    return PROXY["glActiveTexture"](texture)


def glAttachShader(program, shader):
    return PROXY["glAttachShader"](program, shader)


def glBindAttribLocation(program, index, name):
    return PROXY["glBindAttribLocation"](program, index, name)


def glBindBuffer(target, buffer):
    return PROXY["glBindBuffer"](target, buffer)


def glBindFramebuffer(target, framebuffer):
    return PROXY["glBindFramebuffer"](target, framebuffer)


def glBindRenderbuffer(target, renderbuffer):
    return PROXY["glBindRenderbuffer"](target, renderbuffer)


def glBindTexture(target, texture):
    return PROXY["glBindTexture"](target, texture)


def glBlendColor(red, green, blue, alpha):
    return PROXY["glBlendColor"](red, green, blue, alpha)


def glBlendEquation(mode):
    return PROXY["glBlendEquation"](mode)


def glBlendEquationSeparate(modeRGB, modeAlpha):
    return PROXY["glBlendEquationSeparate"](modeRGB, modeAlpha)


def glBlendFunc(sfactor, dfactor):
    return PROXY["glBlendFunc"](sfactor, dfactor)


def glBlendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha):
    return PROXY["glBlendFuncSeparate"](srcRGB, dstRGB, srcAlpha, dstAlpha)


def glBufferData(target, data, usage):
    return PROXY["glBufferData"](target, data, usage)


def glBufferSubData(target, offset, data):
    return PROXY["glBufferSubData"](target, offset, data)


def glCheckFramebufferStatus(target):
    return PROXY["glCheckFramebufferStatus"](target)


def glClear(mask):
    return PROXY["glClear"](mask)


def glClearColor(red, green, blue, alpha):
    return PROXY["glClearColor"](red, green, blue, alpha)


def glClearDepth(depth):
    return PROXY["glClearDepth"](depth)


def glClearStencil(s):
    return PROXY["glClearStencil"](s)


def glColorMask(red, green, blue, alpha):
    return PROXY["glColorMask"](red, green, blue, alpha)


def glCompileShader(shader):
    return PROXY["glCompileShader"](shader)


def glCompressedTexImage2D(target, level, internalformat, width, height, border, data):
    return PROXY["glCompressedTexImage2D"](target, level, internalformat, width, height, border, data)


def glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    return PROXY["glCompressedTexSubImage2D"](target, level, xoffset, yoffset, width, height, format, data)


def glCopyTexImage2D(target, level, internalformat, x, y, width, height, border):
    return PROXY["glCopyTexImage2D"](target, level, internalformat, x, y, width, height, border)


def glCopyTexSubImage2D(target, level, xoffset, yoffset, x, y, width, height):
    return PROXY["glCopyTexSubImage2D"](target, level, xoffset, yoffset, x, y, width, height)


def glCreateProgram():
    return PROXY["glCreateProgram"]()


def glCreateShader(type):
    return PROXY["glCreateShader"](type)


def glCullFace(mode):
    return PROXY["glCullFace"](mode)


def glDeleteBuffer(buffer):
    return PROXY["glDeleteBuffer"](buffer)


def glDeleteFramebuffer(framebuffer):
    return PROXY["glDeleteFramebuffer"](framebuffer)


def glDeleteProgram(program):
    return PROXY["glDeleteProgram"](program)


def glDeleteRenderbuffer(renderbuffer):
    return PROXY["glDeleteRenderbuffer"](renderbuffer)


def glDeleteShader(shader):
    return PROXY["glDeleteShader"](shader)


def glDeleteTexture(texture):
    return PROXY["glDeleteTexture"](texture)


def glDepthFunc(func):
    return PROXY["glDepthFunc"](func)


def glDepthMask(flag):
    return PROXY["glDepthMask"](flag)


def glDepthRange(zNear, zFar):
    return PROXY["glDepthRange"](zNear, zFar)


def glDetachShader(program, shader):
    return PROXY["glDetachShader"](program, shader)


def glDisable(cap):
    return PROXY["glDisable"](cap)


def glDisableVertexAttribArray(index):
    return PROXY["glDisableVertexAttribArray"](index)


def glDrawArrays(mode, first, count):
    return PROXY["glDrawArrays"](mode, first, count)


def glDrawElements(mode, count, type, offset):
    return PROXY["glDrawElements"](mode, count, type, offset)


def glEnable(cap):
    return PROXY["glEnable"](cap)


def glEnableVertexAttribArray(index):
    return PROXY["glEnableVertexAttribArray"](index)


def glFinish():
    return PROXY["glFinish"]()


def glFlush():
    return PROXY["glFlush"]()


def glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer):
    return PROXY["glFramebufferRenderbuffer"](target, attachment, renderbuffertarget, renderbuffer)


def glFramebufferTexture2D(target, attachment, textarget, texture, level):
    return PROXY["glFramebufferTexture2D"](target, attachment, textarget, texture, level)


def glFrontFace(mode):
    return PROXY["glFrontFace"](mode)


def glCreateBuffer():
    return PROXY["glCreateBuffer"]()


def glCreateFramebuffer():
    return PROXY["glCreateFramebuffer"]()


def glCreateRenderbuffer():
    return PROXY["glCreateRenderbuffer"]()


def glCreateTexture():
    return PROXY["glCreateTexture"]()


def glGenerateMipmap(target):
    return PROXY["glGenerateMipmap"](target)


def glGetActiveAttrib(program, index):
    return PROXY["glGetActiveAttrib"](program, index)


def glGetActiveUniform(program, index):
    return PROXY["glGetActiveUniform"](program, index)


def glGetAttachedShaders(program):
    return PROXY["glGetAttachedShaders"](program)


def glGetAttribLocation(program, name):
    return PROXY["glGetAttribLocation"](program, name)


def _glGetBooleanv(pname):
    return PROXY["_glGetBooleanv"](pname)


def glGetBufferParameter(target, pname):
    return PROXY["glGetBufferParameter"](target, pname)


def glGetError():
    return PROXY["glGetError"]()


def _glGetFloatv(pname):
    return PROXY["_glGetFloatv"](pname)


def glGetFramebufferAttachmentParameter(target, attachment, pname):
    return PROXY["glGetFramebufferAttachmentParameter"](target, attachment, pname)


def _glGetIntegerv(pname):
    return PROXY["_glGetIntegerv"](pname)


def glGetProgramInfoLog(program):
    return PROXY["glGetProgramInfoLog"](program)


def glGetProgramParameter(program, pname):
    return PROXY["glGetProgramParameter"](program, pname)


def glGetRenderbufferParameter(target, pname):
    return PROXY["glGetRenderbufferParameter"](target, pname)


def glGetShaderInfoLog(shader):
    return PROXY["glGetShaderInfoLog"](shader)


def glGetShaderPrecisionFormat(shadertype, precisiontype):
    return PROXY["glGetShaderPrecisionFormat"](shadertype, precisiontype)


def glGetShaderSource(shader):
    return PROXY["glGetShaderSource"](shader)


def glGetShaderParameter(shader, pname):
    return PROXY["glGetShaderParameter"](shader, pname)


def glGetParameter(pname):
    return PROXY["glGetParameter"](pname)


def glGetTexParameter(target, pname):
    return PROXY["glGetTexParameter"](target, pname)


def glGetUniform(program, location):
    return PROXY["glGetUniform"](program, location)


def glGetUniformLocation(program, name):
    return PROXY["glGetUniformLocation"](program, name)


def glGetVertexAttrib(index, pname):
    return PROXY["glGetVertexAttrib"](index, pname)


def glGetVertexAttribOffset(index, pname):
    return PROXY["glGetVertexAttribOffset"](index, pname)


def glHint(target, mode):
    return PROXY["glHint"](target, mode)


def glIsBuffer(buffer):
    return PROXY["glIsBuffer"](buffer)


def glIsEnabled(cap):
    return PROXY["glIsEnabled"](cap)


def glIsFramebuffer(framebuffer):
    return PROXY["glIsFramebuffer"](framebuffer)


def glIsProgram(program):
    return PROXY["glIsProgram"](program)


def glIsRenderbuffer(renderbuffer):
    return PROXY["glIsRenderbuffer"](renderbuffer)


def glIsShader(shader):
    return PROXY["glIsShader"](shader)


def glIsTexture(texture):
    return PROXY["glIsTexture"](texture)


def glLineWidth(width):
    return PROXY["glLineWidth"](width)


def glLinkProgram(program):
    return PROXY["glLinkProgram"](program)


def glPixelStorei(pname, param):
    return PROXY["glPixelStorei"](pname, param)


def glPolygonOffset(factor, units):
    return PROXY["glPolygonOffset"](factor, units)


def glReadPixels(x, y, width, height, format, type):
    return PROXY["glReadPixels"](x, y, width, height, format, type)


def glRenderbufferStorage(target, internalformat, width, height):
    return PROXY["glRenderbufferStorage"](target, internalformat, width, height)


def glSampleCoverage(value, invert):
    return PROXY["glSampleCoverage"](value, invert)


def glScissor(x, y, width, height):
    return PROXY["glScissor"](x, y, width, height)


def glShaderSource(shader, source):
    return PROXY["glShaderSource"](shader, source)


def glStencilFunc(func, ref, mask):
    return PROXY["glStencilFunc"](func, ref, mask)


def glStencilFuncSeparate(face, func, ref, mask):
    return PROXY["glStencilFuncSeparate"](face, func, ref, mask)


def glStencilMask(mask):
    return PROXY["glStencilMask"](mask)


def glStencilMaskSeparate(face, mask):
    return PROXY["glStencilMaskSeparate"](face, mask)


def glStencilOp(fail, zfail, zpass):
    return PROXY["glStencilOp"](fail, zfail, zpass)


def glStencilOpSeparate(face, fail, zfail, zpass):
    return PROXY["glStencilOpSeparate"](face, fail, zfail, zpass)


def glTexImage2D(target, level, internalformat, format, type, pixels):
    return PROXY["glTexImage2D"](target, level, internalformat, format, type, pixels)


def glTexParameterf(target, pname, param):
    return PROXY["glTexParameterf"](target, pname, param)
def glTexParameteri(target, pname, param):
    return PROXY["glTexParameteri"](target, pname, param)


def glTexSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    return PROXY["glTexSubImage2D"](target, level, xoffset, yoffset, format, type, pixels)


def glUniform1f(location, v1):
    return PROXY["glUniform1f"](location, v1)
def glUniform2f(location, v1, v2):
    return PROXY["glUniform2f"](location, v1, v2)
def glUniform3f(location, v1, v2, v3):
    return PROXY["glUniform3f"](location, v1, v2, v3)
def glUniform4f(location, v1, v2, v3, v4):
    return PROXY["glUniform4f"](location, v1, v2, v3, v4)
def glUniform1i(location, v1):
    return PROXY["glUniform1i"](location, v1)
def glUniform2i(location, v1, v2):
    return PROXY["glUniform2i"](location, v1, v2)
def glUniform3i(location, v1, v2, v3):
    return PROXY["glUniform3i"](location, v1, v2, v3)
def glUniform4i(location, v1, v2, v3, v4):
    return PROXY["glUniform4i"](location, v1, v2, v3, v4)
def glUniform1fv(location, count, values):
    return PROXY["glUniform1fv"](location, count, values)
def glUniform2fv(location, count, values):
    return PROXY["glUniform2fv"](location, count, values)
def glUniform3fv(location, count, values):
    return PROXY["glUniform3fv"](location, count, values)
def glUniform4fv(location, count, values):
    return PROXY["glUniform4fv"](location, count, values)
def glUniform1iv(location, count, values):
    return PROXY["glUniform1iv"](location, count, values)
def glUniform2iv(location, count, values):
    return PROXY["glUniform2iv"](location, count, values)
def glUniform3iv(location, count, values):
    return PROXY["glUniform3iv"](location, count, values)
def glUniform4iv(location, count, values):
    return PROXY["glUniform4iv"](location, count, values)


def glUniformMatrix2fv(location, count, transpose, values):
    return PROXY["glUniformMatrix2fv"](location, count, transpose, values)
def glUniformMatrix3fv(location, count, transpose, values):
    return PROXY["glUniformMatrix3fv"](location, count, transpose, values)
def glUniformMatrix4fv(location, count, transpose, values):
    return PROXY["glUniformMatrix4fv"](location, count, transpose, values)


def glUseProgram(program):
    return PROXY["glUseProgram"](program)


def glValidateProgram(program):
    return PROXY["glValidateProgram"](program)


def glVertexAttrib1f(index, v1):
    return PROXY["glVertexAttrib1f"](index, v1)
def glVertexAttrib2f(index, v1, v2):
    return PROXY["glVertexAttrib2f"](index, v1, v2)
def glVertexAttrib3f(index, v1, v2, v3):
    return PROXY["glVertexAttrib3f"](index, v1, v2, v3)
def glVertexAttrib4f(index, v1, v2, v3, v4):
    return PROXY["glVertexAttrib4f"](index, v1, v2, v3, v4)


def glVertexAttribPointer(indx, size, type, normalized, stride, offset):
    return PROXY["glVertexAttribPointer"](indx, size, type, normalized, stride, offset)


def glViewport(x, y, width, height):
    return PROXY["glViewport"](x, y, width, height)


