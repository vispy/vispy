# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import ctypes
import numpy as np
import OpenGL.GL as gl

from debug import log
from globject import GLObject
from buffer import VertexBuffer
from texture import Texture1D, Texture2D


# ------------------------------------------------------------- gl_typeinfo ---
gl_typeinfo = {
    gl.GL_FLOAT        : ( 1, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC2   : ( 2, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC3   : ( 3, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC4   : ( 4, gl.GL_FLOAT,        np.float32),
    gl.GL_INT          : ( 1, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC2     : ( 2, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC3     : ( 3, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC4     : ( 4, gl.GL_INT,          np.int32),
    gl.GL_BOOL         : ( 1, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC2    : ( 2, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC3    : ( 3, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC4    : ( 4, gl.GL_BOOL,         np.bool),
    gl.GL_FLOAT_MAT2   : ( 4, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_MAT3   : ( 9, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_MAT4   : (16, gl.GL_FLOAT,        np.float32),
    gl.GL_SAMPLER_1D   : ( 1, gl.GL_UNSIGNED_INT, np.uint32),
    gl.GL_SAMPLER_2D   : ( 1, gl.GL_UNSIGNED_INT, np.uint32)
}



# ---------------------------------------------------------- Variable class ---
class Variable(GLObject):
    """ A variable is an interface between a program and some data """

    def __init__(self, program, name, gtype):
        """ Initialize the data into default state """

        # Make sure variable type is allowed (for ES 2.0 shader)
        if gtype not in [gl.GL_FLOAT,      gl.GL_FLOAT_VEC2,
                         gl.GL_FLOAT_VEC3, gl.GL_FLOAT_VEC4,
                         gl.GL_INT,        gl.GL_BOOL,
                         gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3,
                         gl.GL_FLOAT_MAT4, gl.GL_SAMPLER_1D,
                         gl.GL_SAMPLER_2D]:
            raise TypeError("Unknown variable type")

        GLObject.__init__(self)

        # Program this variable belongs to
        self._program = program

        # Name of this variable in the program
        self._name = name

        # Build dtype
        size, _, base = gl_typeinfo[gtype]
        self._dtype = (name,base,size)

        # GL type
        self._gtype = gtype

        # CPU data
        self._data = None

        # Whether this variable is active
        self._active = True


    @property
    def name(self):
        """ Variable name """

        return self._name


    @property
    def program(self):
        """ Program this variable belongs to """

        return self._program


    @property
    def gtype(self):
        """ Type of the underlying variable (as a GL constant) """

        return self._gtype

    @property
    def dtype(self):
        """ Equivalent dtype of the variable """

        return self._dtype


    @property
    def active(self):
        """ Whether this variable is active in the program """
        return self._active


    @active.setter
    def active(self, active):
        """ Whether this variable is active in the program """
        self._active = active


    @property
    def data(self):
        """ CPU data """

        return self._data



# ----------------------------------------------------------- Uniform class ---
class Uniform(Variable):
    """ A Uniform represents a program uniform variable. """

    _ufunctions = {
        gl.GL_FLOAT:        gl.glUniform1fv,
        gl.GL_FLOAT_VEC2:   gl.glUniform2fv,
        gl.GL_FLOAT_VEC3:   gl.glUniform3fv,
        gl.GL_FLOAT_VEC4:   gl.glUniform4fv,
        gl.GL_INT:          gl.glUniform1iv,
        gl.GL_BOOL:         gl.glUniform1iv,
        gl.GL_FLOAT_MAT2:   gl.glUniformMatrix2fv,
        gl.GL_FLOAT_MAT3:   gl.glUniformMatrix3fv,
        gl.GL_FLOAT_MAT4:   gl.glUniformMatrix4fv,
        gl.GL_SAMPLER_1D:   gl.glUniform1i,
        gl.GL_SAMPLER_2D:   gl.glUniform1i,
    }


    def __init__(self, program, name, gtype):
        """ Initialize the input into default state """

        Variable.__init__(self, program, name, gtype)
        size, _, dtype = gl_typeinfo[self._gtype]
        self._data = np.zeros(size, dtype)
        self._ufunction = Uniform._ufunctions[self._gtype]
        self._unit = -1


    def set_data(self, data):
        """ Set data (no upload) """

        # Textures need special handling
        if self._gtype == gl.GL_SAMPLER_1D:
            if isinstance(self._data, Texture1D):
                self._data.set_data(data)

            # Automatic texture creation if required
            elif not isinstance(data,Texture1D):
                data = np.array(data,copy=False)
                if data.dtype in [np.float16, np.float32, np.float64]:
                    self._data = Texture1D(data=data.astype(np.float32))
                else:
                    self._data = Texture1D(data=data.astype(np.uint8))
            else:
                self._data = data
        elif self._gtype == gl.GL_SAMPLER_2D:
            if isinstance(self._data, Texture2D):
                self._data.set_data(data)

            # Automatic texture creation if required
            elif not isinstance(data,Texture2D):
                data = np.array(data,copy=False)
                if data.dtype in [np.float16, np.float32, np.float64]:
                    self._data = Texture2D(data=data.astype(np.float32))
                else:
                    self._data = Texture2D(data=data.astype(np.uint8))
            else:
                self._data = data
        else:
            self._data[...] = np.array(data,copy=False).ravel()

        self._need_update = True


    def _activate(self):
        if self._gtype in (gl.GL_SAMPLER_1D, gl.GL_SAMPLER_2D):
            if self.data is not None:
                log("GPU: Active texture is %d" % self._unit)
                gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
                self.data.activate()

    def _update(self):

        # Check active status (mandatory)
        if not self._active:
            raise RuntimeError("Uniform variable is not active")

        # WARNING : Uniform are supposed to keep their value between program
        #           activation/deactivation (from the GL documentation). It has
        #           been tested on some machines but if it is not the case on
        #           every machine, we can expect nasty bugs from this early
        #           return

        # Matrices (need a transpose argument)
        if self._gtype in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4):
            # OpenGL ES 2.0 does not support transpose
            transpose = False
            self._ufunction(self._handle, 1, transpose, self._data)

        # Textures (need to get texture count)
        elif self._gtype in (gl.GL_SAMPLER_1D, gl.GL_SAMPLER_2D):
            # texture = self.data
            # log("GPU: Active texture is %d" % self._unit)
            # gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            # gl.glBindTexture(texture.target, texture.handle)
            gl.glUniform1i(self._handle, self._unit)

        # Regular uniform
        else:
            self._ufunction(self._handle, 1, self._data)


    def _create(self):
        """ Create uniform on GPU (get handle) """

        self._handle = gl.glGetUniformLocation(self._program.handle, self._name)




# --------------------------------------------------------- Attribute class ---
class Attribute(Variable):
    """ An Attribute represents a program attribute variable """

    _afunctions = {
        gl.GL_FLOAT:      gl.glVertexAttrib1f,
        gl.GL_FLOAT_VEC2: gl.glVertexAttrib2f,
        gl.GL_FLOAT_VEC3: gl.glVertexAttrib3f,
        gl.GL_FLOAT_VEC4: gl.glVertexAttrib4f
    }

    def __init__(self, program, name, gtype):
        """ Initialize the input into default state """

        Variable.__init__(self, program, name, gtype)

        # Number of elements this attribute links to (in the attached buffer)
        self._size = 0

        # Whether this attribure is generic
        self._generic = False


    def set_data(self, data):
        """ Set data (deferred operation) """

        # Data is a tuple with size <= 4, we assume this designates a generate
        # vertex attribute.
        if (type(data) in (float,int) or
            (type(data) in (tuple,list) and len(data) in [1,2,3,4] and data[0] in (float,int))):

            # Let numpy convert the data for us
            _, _, dtype = gl_typeinfo[self._gtype]
            self._data = np.array(data).astype(dtype)
            self._generic = True
            self._need_update = True
            self._afunction = Attribute._afunctions[self._gtype]
            return

        # If we already have a VertexBuffer
        elif isinstance(self._data, VertexBuffer):
            self._data[...] = data

        # For array-like, we need to build a proper VertexBuffer to be able to
        # upload it later to GPU memory.
        elif not isinstance(data, VertexBuffer):
            name,base,count = self.dtype
            data = np.array(data,dtype=base,copy=False)
            data = data.ravel().view([self.dtype])
            # WARNING : transform data with the right type
            # data = np.array(data,copy=False)
            self._data = VertexBuffer(data)
        else:
            self._data = data
        self._generic = False


    def _activate(self):
        if isinstance(self.data,VertexBuffer):
            self.data.activate()

    def _update(self):
        """ Actual upload of data to GPU memory  """

        log("GPU: Updating %s" % self.name)

        # Generic vertex attribute (all vertices receive the same value)
        if self._generic:
            if self._handle >= 0:
                gl.glDisableVertexAttribArray(self._handle)
                self._afunction(self._handle, *self._data)

        # Direct upload
        #elif isinstance(self._data, ClientVertexBuffer):
            # Tell OpenGL to use the array and not the glVertexAttrib* value
            # gl.glEnableVertexAttribArray(self._loc)
            # Disable any VBO
            # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            # Early exit (pointer to CPU-data is still known by Program)
            #if not self._dirty:
            #    return
            # Get numpy array from its container
            #data = self._data.data

            # Check attribute format against data format
            #size, gtype, _ = gl_typeinfo[self._gtype]
            #if self._gtype != self._data._gtype:
            #    raise ValueError("Data not compatible with attribute type")
            #offset = 0
            #stride = self._data.stride
            # Apply (first disable any previous VertexBuffer)
            #gl.glVertexAttribPointer(self._loc, size, gtype, False, stride, data)

        # Regular vertex buffer
        elif self._handle >= 0:
            if self._need_update:
                self.data.update()

            # Get relevant information from gl_typeinfo
            size, gtype, dtype = gl_typeinfo[self._gtype]
            stride = self.data.stride

            # Make offset a pointer, or it will be interpreted as a small array
            offset = ctypes.c_void_p(self.data.offset)

            gl.glEnableVertexAttribArray(self.handle)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.data.handle)
            gl.glVertexAttribPointer(self.handle, size, gtype,  gl.GL_FALSE, stride, offset)


    def _create(self):
        """ Create attribute on GPU (get handle) """

        self._handle = gl.glGetAttribLocation(self._program.handle, self.name)


    @property
    def size(self):
        """ Size of the underlying vertex buffer """

        if self._data is None:
            return 0
        return self._data.size
