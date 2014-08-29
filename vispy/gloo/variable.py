# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from . import gl
from .globject import GLObject
from .buffer import VertexBuffer, DataBufferView
from .texture import BaseTexture, Texture2D, Texture3D, GL_SAMPLER_3D
from .framebuffer import RenderBuffer
from ..util import logger
from .util import check_variable


# ------------------------------------------------------------- gl_typeinfo ---
gl_typeinfo = {
    gl.GL_FLOAT: (1, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC2: (2, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC3: (3, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_VEC4: (4, gl.GL_FLOAT,        np.float32),
    gl.GL_INT: (1, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC2: (2, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC3: (3, gl.GL_INT,          np.int32),
    gl.GL_INT_VEC4: (4, gl.GL_INT,          np.int32),
    gl.GL_BOOL: (1, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC2: (2, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC3: (3, gl.GL_BOOL,         np.bool),
    gl.GL_BOOL_VEC4: (4, gl.GL_BOOL,         np.bool),
    gl.GL_FLOAT_MAT2: (4, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_MAT3: (9, gl.GL_FLOAT,        np.float32),
    gl.GL_FLOAT_MAT4: (16, gl.GL_FLOAT,        np.float32),
    #    gl.GL_SAMPLER_1D   : ( 1, gl.GL_UNSIGNED_INT, np.uint32),
    gl.GL_SAMPLER_2D: (1, gl.GL_UNSIGNED_INT, np.uint32),
    GL_SAMPLER_3D: (1, gl.GL_UNSIGNED_INT, np.uint32)
}


# ---------------------------------------------------------- Variable class ---
class Variable(GLObject):
    """ A variable is an interface between a program and some data 
    
    For internal use
    
    Parameters
    ----------
    
    program : Program
        The Program instance to which the data applies
    name : str
        The variable name
    gtype : ENUM
        The type of the variable: GL_FLOAT, GL_FLOAT_VEC2, GL_FLOAT_VEC3,
        GL_FLOAT_VEC4, GL_INT, GL_BOOL, GL_FLOAT_MAT2, GL_FLOAT_MAT3,
        GL_FLOAT_MAT4, gl.GL_SAMPLER_2D, or GL_SAMPLER_3D
    
    """

    def __init__(self, program, name, gtype):
        """ Initialize the data into default state """

        # Make sure variable type is allowed (for ES 2.0 shader)
        if gtype not in [gl.GL_FLOAT,
                         gl.GL_FLOAT_VEC2,
                         gl.GL_FLOAT_VEC3,
                         gl.GL_FLOAT_VEC4,
                         gl.GL_INT,
                         gl.GL_BOOL,
                         gl.GL_FLOAT_MAT2,
                         gl.GL_FLOAT_MAT3,
                         gl.GL_FLOAT_MAT4,
                         #                         gl.GL_SAMPLER_1D,
                         gl.GL_SAMPLER_2D,
                         GL_SAMPLER_3D]:
            raise TypeError("Unknown variable type")

        GLObject.__init__(self)

        # Program this variable belongs to
        self._program = program

        # Name of this variable in the program
        self._name = name
        check = check_variable(name)
        if check:
            logger.warning('Invalid variable name "%s". (%s)'
                           % (name, check))

        # Build dtype
        size, _, base = gl_typeinfo[gtype]
        self._dtype = (name, base, size)

        # GL type
        self._gtype = gtype

        # CPU data
        self._data = None

        # Whether this variable is actually being used by GLSL
        self._enabled = True

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
    def enabled(self):
        """ Whether this variable is being used by the program """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """ Whether this variable is being used by the program """
        self._enabled = bool(enabled)

    @property
    def data(self):
        """ CPU data """
        return self._data

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)


# ----------------------------------------------------------- Uniform class ---
class Uniform(Variable):
    """ A Uniform represents a program uniform variable. 
    
    See Variable.
    """

    # todo: store function names instead of GL proxy function (faster)
    _ufunctions = {
        gl.GL_FLOAT:        gl.proxy.glUniform1fv,
        gl.GL_FLOAT_VEC2:   gl.proxy.glUniform2fv,
        gl.GL_FLOAT_VEC3:   gl.proxy.glUniform3fv,
        gl.GL_FLOAT_VEC4:   gl.proxy.glUniform4fv,
        gl.GL_INT:          gl.proxy.glUniform1iv,
        gl.GL_BOOL:         gl.proxy.glUniform1iv,
        gl.GL_FLOAT_MAT2:   gl.proxy.glUniformMatrix2fv,
        gl.GL_FLOAT_MAT3:   gl.proxy.glUniformMatrix3fv,
        gl.GL_FLOAT_MAT4:   gl.proxy.glUniformMatrix4fv,
        #        gl.GL_SAMPLER_1D:   gl.proxy.glUniform1i,
        gl.GL_SAMPLER_2D:   gl.proxy.glUniform1i,
        GL_SAMPLER_3D:   gl.proxy.glUniform1i,
    }

    def __init__(self, program, name, gtype):
        """ Initialize the input into default state """

        Variable.__init__(self, program, name, gtype)
        size, _, dtype = gl_typeinfo[self._gtype]
        self._data = np.zeros(size, dtype)
        self._ufunction = Uniform._ufunctions[self._gtype]
        self._unit = -1
        self._need_update = False

    def set_data(self, data):
        """ Set data (no upload) """
        if self._gtype == gl.GL_SAMPLER_2D:
            if isinstance(data, Texture2D):
                self._data = data
            elif isinstance(self._data, Texture2D):
                self._data.set_data(data)
            elif isinstance(data, RenderBuffer):
                self._data = data
            else:
                # Automatic texture creation if required
                data = np.array(data, copy=False)
                if data.dtype in [np.float16, np.float32, np.float64]:
                    self._data = Texture2D(data=data.astype(np.float32))
                else:
                    self._data = Texture2D(data=data.astype(np.uint8))
        elif self._gtype == GL_SAMPLER_3D:
            if isinstance(data, Texture3D):
                self._data = data
            elif isinstance(self._data, Texture3D):
                self._data.set_data(data)
            elif isinstance(data, RenderBuffer):
                self._data = data
            else:
                # Automatic texture creation if required
                data = np.array(data, copy=False)
                if data.dtype in [np.float16, np.float32, np.float64]:
                    self._data = Texture3D(data=data.astype(np.float32))
                else:
                    self._data = Texture3D(data=data.astype(np.uint8))
        else:
            self._data[...] = np.array(data, copy=False).ravel()

        self._need_update = True

    def _activate(self):
        # if self._gtype in (gl.GL_SAMPLER_1D, gl.GL_SAMPLER_2D):
        if self._gtype in (gl.GL_SAMPLER_2D, GL_SAMPLER_3D):
            logger.debug("GPU: Active texture is %d" % self._unit)
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            if isinstance(self._data, BaseTexture):
                self._data.activate()

        # Update if necessary. OpenGL stores uniform values at the Program
        # object, so they only have to be set once.
        if self._need_update:
            self._update()
            self._need_update = False

    def _deactivate(self):
        if self._gtype in (gl.GL_SAMPLER_2D, GL_SAMPLER_3D):
            #gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            if self.data is not None:
                self.data.deactivate()

    def _update(self):

        # Check active status (mandatory)
        if not self._enabled:
            raise RuntimeError("Uniform %r is not active" % self.name)
        if self._data is None:
            raise RuntimeError("Uniform data not set for %r" % self.name)
        
        # Matrices (need a transpose argument)
        if self._gtype in (gl.GL_FLOAT_MAT2,
                           gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4):
            # OpenGL ES 2.0 does not support transpose
            transpose = False
            self._ufunction(self._handle, 1, transpose, self._data)

        # Textures (need to get texture count)
        # elif self._gtype in (gl.GL_SAMPLER_1D, gl.GL_SAMPLER_2D):
        elif self._gtype in (gl.GL_SAMPLER_2D, GL_SAMPLER_3D):
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
        self._handle = gl.glGetUniformLocation(
            self._program.handle, self._name)
    
    def _delete(self):
        pass  # No need to delete variables; they are not really *objects*


# --------------------------------------------------------- Attribute class ---
class Attribute(Variable):
    """ An Attribute represents a program attribute variable 
    
    See Variable.
    """

    _afunctions = {
        gl.GL_FLOAT:      gl.proxy.glVertexAttrib1f,
        gl.GL_FLOAT_VEC2: gl.proxy.glVertexAttrib2f,
        gl.GL_FLOAT_VEC3: gl.proxy.glVertexAttrib3f,
        gl.GL_FLOAT_VEC4: gl.proxy.glVertexAttrib4f
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
        
        isnumeric = isinstance(data, (float, int))
        
        if (isinstance(data, VertexBuffer) or
            (isinstance(data, DataBufferView) and 
             isinstance(data.base, VertexBuffer))):
            # New vertex buffer
            self._data = data
        elif isinstance(self._data, VertexBuffer):
            # We already have a vertex buffer
            self._data.set_data(data)
        elif (isnumeric or (isinstance(data, (tuple, list)) and
                            len(data) in (1, 2, 3, 4) and
                            isinstance(data[0], (float, int)))):
            # Data is a tuple with size <= 4, we assume this designates
            # a generate vertex attribute.
            # Let numpy convert the data for us
            _, _, dtype = gl_typeinfo[self._gtype]
            self._data = np.array(data).astype(dtype)
            self._generic = True
            #self._need_update = True
            self._afunction = Attribute._afunctions[self._gtype]
            return
        else:
            # For array-like, we need to build a proper VertexBuffer
            # to be able to upload it later to GPU memory.
            name, base, count = self.dtype
            data = np.array(data, dtype=base, copy=False)
            data = data.ravel().view([self.dtype])
            # WARNING : transform data with the right type
            # data = np.array(data,copy=False)
            self._data = VertexBuffer(data)
        
        self._generic = False

    def _activate(self):
        # Update always, attributes are not stored at the Program object
        self._update()
    
    def _deactivate(self):
        if isinstance(self.data, VertexBuffer):
            self.data.deactivate()
    
    def _update(self):
        """ Actual upload of data to GPU memory  """

        #logger.debug("GPU: Updating %s" % self.name)
        
        # Check active status (mandatory)
        if not self._enabled:
            raise RuntimeError("Attribute %r is not active" % self.name)
        if self._data is None:
            raise RuntimeError("Attribute data not set for %r" % self.name)
        
        # Generic vertex attribute (all vertices receive the same value)
        if self._generic:
            if self._handle >= 0:
                gl.glDisableVertexAttribArray(self._handle)
                self._afunction(self._handle, *self._data)

        # Regular vertex buffer
        elif self._handle >= 0:
            
            # Activate the VBO
            self.data.activate()
            
            # Get relevant information from gl_typeinfo
            size, gtype, dtype = gl_typeinfo[self._gtype]
            stride = self.data.stride
            offset = self.data.offset

            gl.glEnableVertexAttribArray(self.handle)
            gl.glVertexAttribPointer(
                self.handle, size, gtype, gl.GL_FALSE, stride, offset)

    def _create(self):
        """ Create attribute on GPU (get handle) """
        self._handle = gl.glGetAttribLocation(self._program.handle, self.name)
    
    def _delete(self):
        pass  # No need to delete variables; they are not really *objects*
    
    @property
    def size(self):
        """ Size of the underlying vertex buffer """

        if self._data is None:
            return 0
        return self._data.size
