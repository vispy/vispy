# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" 
This module contains manual annotations for the gl backends. Together
with the header files, we can generatre the full ES 2.0 API.

Every function-annotations consists of sections that apply to one or
more backends. If no backends are specified in the first section, it
applies to all backends.
"""

import ctypes


## bind / gen / delete stuff

def deleteBuffer(buffer):
    # --- gl es
    n = 1  
    buffers = (ctypes.c_uint*n)(buffer)  
    ()  
    # --- pyopengl
    GL.glDeleteBuffers(1, [buffer])

def deleteFramebuffer(framebuffer):
    # --- gl es
    n = 1  
    framebuffers = (ctypes.c_uint*n)(framebuffer)  
    ()
    # --- pyopengl
    FBO.glDeleteFramebuffers(1, [framebuffer])

def deleteRenderbuffer(renderbuffer):
    # --- gl es
    n = 1  
    renderbuffers = (ctypes.c_uint*n)(renderbuffer)  
    ()
    # --- pyopengl
    FBO.glDeleteRenderbuffers(1, [renderbuffer])

def deleteTexture(texture):
    # --- gl es
    n = 1  
    textures = (ctypes.c_uint*n)(texture)  
    ()
    # --- pyopengl
    GL.glDeleteTextures([texture])


def createBuffer():
    # --- gl es
    n = 1
    buffers = (ctypes.c_uint*n)()
    ()  
    return buffers[0]
    # --- pyopengl
    return GL.glGenBuffers(1)
    # --- mock
    return 1

def createFramebuffer():
    # --- gl es
    n = 1
    framebuffers = (ctypes.c_uint*n)()
    ()
    return framebuffers[0]
    # --- pyopengl
    return FBO.glGenFramebuffers(1)
    # --- mock
    return 1

def createRenderbuffer():
    # --- gl es
    n = 1
    renderbuffers = (ctypes.c_uint*n)()
    ()
    return renderbuffers[0]
    # --- pyopengl
    return FBO.glGenRenderbuffers(1)
    # --- mock
    return 1

def createTexture():
    # --- gl es
    n = 1
    textures = (ctypes.c_uint*n)()
    ()
    return textures[0]
    # --- pyopengl
    return GL.glGenTextures(1)
    # --- mock
    return 1


## Image stuff

def texImage2D(target, level, internalformat, format, type, pixels):
    border = 0
    # --- gl es
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
    ()
    # --- pyopengl
    if isinstance(pixels, (tuple, list)):
        height, width = pixels
        pixels = None
    else:
        height, width = pixels.shape[:2]
    GL.glTexImage2D(target, level, internalformat, width, height, border, format, type, pixels)
    


def texSubImage2D(target, level, xoffset, yoffset, format, type, pixels):
    # --- gl es
    if not pixels.flags['C_CONTIGUOUS']:
        pixels = pixels.copy('C')
    pixels_ = pixels
    pixels = pixels_.ctypes.data
    height, width = pixels_.shape[:2]
    ()
    # --- pyopengl
    height, width = pixels.shape[:2]
    GL.glTexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels)


def readPixels(x, y, width, height, format, type):
    # --- gl es mock
    # GL_ALPHA, GL_RGB, GL_RGBA
    t = {6406:1, 6407:3, 6408:4}[format]
    # GL_UNSIGNED_BYTE, GL_FLOAT
    nb = {5121:1, 5126:4}[type]
    size = int(width*height*t*nb)
    # --- gl es
    pixels = ctypes.create_string_buffer(size)
    ()
    return pixels[:]
    # --- mock
    return size * b'\x00'


def compressedTexImage2D(target, level, internalformat, width, height, border=0, data=None):
    # border = 0  # set in args
    # --- gl es
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    ()
    # --- pyopengl
    size = data.size
    GL.glCompressedTexImage2D(target, level, internalformat, width, height, border, size, data)


def compressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, data):
    # --- gl es
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.size
    data = data_.ctypes.data
    ()
    # --- pyopengl
    size = data.size
    GL.glCompressedTexSubImage2D(target, level, xoffset, yoffset, width, height, format, size, data)


## Buffer data


def bufferData(target, data, usage):
    """ Data can be numpy array or the size of data to allocate.
    """
    # --- gl es
    if isinstance(data, int):
        size = data
        data = ctypes.c_voidp(0)
    else:
        if not data.flags['C_CONTIGUOUS'] or not data.flags['ALIGNED']:
            data = data.copy('C')
        data_ = data
        size = data_.nbytes
        data = data_.ctypes.data
    ()
    # --- pyopengl
    if isinstance(data, int):
        size = data
        data = None
    else:
        size = data.nbytes
    GL.glBufferData(target, size, data, usage)


def bufferSubData(target, offset, data):
    # --- gl es
    if not data.flags['C_CONTIGUOUS']:
        data = data.copy('C')
    data_ = data
    size = data_.nbytes
    data = data_.ctypes.data
    ()
    # --- pyopengl
    size = data.nbytes
    GL.glBufferSubData(target, offset, size, data)


def drawElements(mode, count, type, offset):
    # --- gl es
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
    ()
    # --- pyopengl
    if offset is None:
        offset = ctypes.c_void_p(0)
    elif isinstance(offset, (int, ctypes.c_int)):
        offset = ctypes.c_void_p(int(offset))
    ()


def vertexAttribPointer(indx, size, type, normalized, stride, offset):
    # --- gl es
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
    ()
    # --- pyopengl
    if offset is None:
        offset = ctypes.c_void_p(0)
    elif isinstance(offset, (int, ctypes.c_int)):
        offset = ctypes.c_void_p(int(offset))
    ()


def bindAttribLocation(program, index, name):
    # --- gl es
    name = ctypes.c_char_p(name.encode('utf-8'))
    ()
    # --- pyopengl
    name = name.encode('utf-8')
    ()


## Setters


def shaderSource(shader, source):
    # Some implementation do not like getting a list of single chars
    if isinstance(source, (tuple, list)):
        strings = [s for s in source]
    else:
        strings = [source]
    # --- gl es
    count = len(strings)  
    string = (ctypes.c_char_p*count)(*[s.encode('utf-8') for s in strings])  
    length = (ctypes.c_int*count)(*[len(s) for s in strings])  
    ()
    # --- pyopengl
    GL.glShaderSource(shader, strings)


## Getters

def _getBooleanv(pname):
    # --- gl es
    params = (ctypes.c_bool*1)()
    ()
    return params[0]

def _getIntegerv(pname):
    # --- gl es
    n = 16
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*n)(*[d for i in range(n)])
    ()
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)

def _getFloatv(pname):
    # --- gl es
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    ()
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)

# def _getString(pname):
#     # --- gl es
#     ()
#     return res.value
#     # --- mock
#     return ''


def getParameter(pname):
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
    # --- gl es
    ()
    return ctypes.string_at(res).decode('utf-8') if res else ''
    # --- pyopengl
    res = GL.glGetString(pname)
    return res.decode('utf-8')


def getUniform(program, location):
    # --- gl es
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    ()
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)
    # --- pyopengl
    n = 16
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    GL.glGetUniformfv(program, location, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


def getVertexAttrib(index, pname):
    # --- gl es
    n = 4
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    ()
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)
    # --- pyopengl
    # From PyOpenGL v3.1.0 the glGetVertexAttribfv(index, pname) does
    # work, but it always returns 4 values, with zeros in the empty
    # spaces. We have no way to tell whether they are empty or genuine
    # zeros. Fortunately, pyopengl also supports the old syntax.
    n = 4
    d = float('Inf')
    params = (ctypes.c_float*n)(*[d for i in range(n)])
    GL.glGetVertexAttribfv(index, pname, params)
    params = [p for p in params if p!=d]
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)


def getTexParameter(target, pname):
    # --- gl es
    d = float('Inf')
    params = (ctypes.c_float*1)(d)
    ()
    return params[0]


def getActiveAttrib(program, index):
    # --- gl es pyopengl
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    # --- gl es
    ()
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]
    # --- pyopengl
    # pyopengl has a bug, this is a patch
    GL.glGetActiveAttrib(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]
    # --- mock
    return 'mock_val', 1, 5126


def getVertexAttribOffset(index, pname):
    # --- gl es
    pointer = (ctypes.c_void_p*1)()
    ()
    return pointer[0] or 0
    # --- pyopengl
    try:  # maybe the fixed it
        ()
    except TypeError:
        pointer = (ctypes.c_void_p*1)()
        GL.glGetVertexAttribPointerv(index, pname, pointer)
        return pointer[0] or 0
    # --- mock
    return 0

    
def getActiveUniform(program, index):
    # --- gl es
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    ()
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]
    # --- pyopengl
    name, size, type = GL.glGetActiveUniform(program, index)
    return name.decode('utf-8'), size, type


def getAttachedShaders(program):
    # --- gl es
    maxcount = 256
    count = (ctypes.c_int*1)()
    shaders = (ctypes.c_uint*maxcount)()
    ()
    return tuple(shaders[:count[0]])


def getAttribLocation(program, name):
    # --- gl es
    name = ctypes.c_char_p(name.encode('utf-8'))
    ()
    return res
    # --- pyopengl
    name = name.encode('utf-8')
    ()
    

def getUniformLocation(program, name):
    # --- gl es
    name = ctypes.c_char_p(name.encode('utf-8'))
    ()
    return res
    # --- pyopengl
    name = name.encode('utf-8')
    ()

def getProgramInfoLog(program):
    # --- gl es
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    ()
    return infolog[:length[0]].decode('utf-8')
    # --- pyopengl
    res = GL.glGetProgramInfoLog(program)
    return res.decode('utf-8') if isinstance(res, bytes) else res

def getShaderInfoLog(shader):
    # --- gl es
    bufsize = 1024
    length = (ctypes.c_int*1)()
    infolog = ctypes.create_string_buffer(bufsize)
    ()
    return infolog[:length[0]].decode('utf-8')
    # --- pyopengl
    res = GL.glGetShaderInfoLog(shader)
    return res.decode('utf-8') if isinstance(res, bytes) else res

def getProgramParameter(program, pname):
    # --- gl es
    params = (ctypes.c_int*1)()
    ()
    return params[0]

def getShaderParameter(shader, pname):
    # --- gl es
    params = (ctypes.c_int*1)()
    ()
    return params[0]

def getShaderPrecisionFormat(shadertype, precisiontype):
    # --- gl es
    range = (ctypes.c_int*1)()
    precision = (ctypes.c_int*1)()
    ()
    return range[0], precision[0]

def getShaderSource(shader):
    # --- gl es
    bufsize = 1024*1024
    length = (ctypes.c_int*1)()
    source = (ctypes.c_char*bufsize)()
    ()
    return source.value[:length[0]].decode('utf-8')
    # --- pyopengl
    res = GL.glGetShaderSource(shader)
    return res.decode('utf-8')
    

def getBufferParameter(target, pname):
    # --- gl es
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    ()
    return params[0]


def getFramebufferAttachmentParameter(target, attachment, pname):
    # --- gl es
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    ()
    return params[0]
    # --- pyopengl
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    FBO.glGetFramebufferAttachmentParameteriv(target, attachment, pname, params)
    return params[0]


def getRenderbufferParameter(target, pname):
    # --- gl es
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    ()
    return params[0]
    # --- pyopengl
    d = -2**31  # smallest 32bit integer
    params = (ctypes.c_int*1)(d)
    FBO.glGetRenderbufferParameteriv(target, pname, params)
    return params[0]



## ============================================================================


class FunctionAnnotation:
    def __init__(self, name, args, output):
        self.name = name
        self.args = args
        self.output = output
        self.lines = []  # (line, comment) tuples
    
    def __repr__(self):
        return '<FunctionAnnotation for %s>' % self.name
        
    def get_lines(self, call, backend):
        """ Get the lines for this function based on the given backend. 
        The given API call is inserted at the correct location.
        """
        backend_selector = (backend, )  # first lines are for all backends
        lines = []
        for line in self.lines:
            if line.lstrip().startswith('# ---'):
                backend_selector = line.strip().split(' ')
                continue
            if backend in backend_selector:
                if line.strip() == '()':
                    indent = line.split('(')[0][4:]
                    line = indent + call
                lines.append(line)
        return lines
    
    def is_arg_set(self, name):
        """ Get whether a given variable name is set.
        This allows checking whether a variable that is an input to the C
        function is not an input for the Python function, and may be an output.
        """
        needle = '%s =' % name
        for line, comment in self.lines:
            if line.startswith(needle):
                return True
        else:
            return False



def parse_anotations():
    """ Parse this annotations file and produce a dictionary of
    FunctionAnnotation objects.
    """
    
    functions = {}
    function = None
    
    for line in open(__file__, 'rt').readlines():
        # Stop?
        if '='*40 in line:
            break
        
        if line.startswith('def '):
            name = line.split(' ')[1].split('(')[0]
            args = line.split('(')[1].split(')')[0].split(', ')
            args = [arg for arg in args if arg]
            out =  line.partition('->')[2].strip()
            function = FunctionAnnotation(name, args, out)
            functions[name] = function
            continue
        elif not function:
            continue
        
        # Add line
        line = line.rstrip()
        indent = len(line) - len(line.strip())
        if line.strip() and indent >=4:
            function.lines.append(line)

    return functions


if __name__ == '__main__':
    print(parse_anotations().keys())
    