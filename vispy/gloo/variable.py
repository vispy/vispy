# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Classes for uniform and attribute variables.

These classes are mainly containers, the only gl functionality is
the uploading of gl data to the GPU.

"""

from __future__ import division

import ctypes
import numpy as np

from . import gl
from .buffer import ClientVertexBuffer, VertexBuffer
from .texture import Texture, Texture2D, TextureCubeMap, Texture3D
from ..util import logger


# todo: support arrays of uniforms

gl_typeinfo = {
    gl.GL_FLOAT: (1, gl.GL_FLOAT, np.float32),
    gl.GL_FLOAT_VEC2: (2, gl.GL_FLOAT, np.float32),
    gl.GL_FLOAT_VEC3: (3, gl.GL_FLOAT, np.float32),
    gl.GL_FLOAT_VEC4: (4, gl.GL_FLOAT, np.float32),
    gl.GL_INT: (1, gl.GL_INT, np.int32),
    gl.GL_INT_VEC2: (2, gl.GL_INT, np.int32),
    gl.GL_INT_VEC3: (3, gl.GL_INT, np.int32),
    gl.GL_INT_VEC4: (4, gl.GL_INT, np.int32),
    gl.GL_BOOL: (1, gl.GL_BOOL, np.bool),
    gl.GL_BOOL_VEC2: (2, gl.GL_BOOL, np.bool),
    gl.GL_BOOL_VEC3: (3, gl.GL_BOOL, np.bool),
    gl.GL_BOOL_VEC4: (4, gl.GL_BOOL, np.bool),
    gl.GL_FLOAT_MAT2: (4, gl.GL_FLOAT, np.float32),
    gl.GL_FLOAT_MAT3: (9, gl.GL_FLOAT, np.float32),
    gl.GL_FLOAT_MAT4: (16, gl.GL_FLOAT, np.float32),
    gl.GL_SAMPLER_2D: (1, gl.GL_UNSIGNED_INT, np.uint32),
    gl.ext.GL_SAMPLER_3D: (1, gl.GL_UNSIGNED_INT, np.uint32),
    gl.GL_SAMPLER_CUBE: (1, gl.GL_UNSIGNED_INT, np.uint32), }


class VariableError(RuntimeError):

    """ Raised when something goes wrong that depens on state that was set
    earlier (due to deferred loading).
    """
    pass


class Variable(object):

    """
    A variable is an interface between a program and some data.
    """

    # NOTE: Variable, Uniform, Attribute are FRIENDS of Program,
    # and Program manimpulates the private attributes of these objects.

    # ---------------------------------
    def __init__(self, name, gtype):
        """ Initialize the data into default state """

        # Make sure variable type is allowed (for ES 2.0 shader)
        if gtype not in [gl.GL_FLOAT, gl.GL_FLOAT_VEC2,
                         gl.GL_FLOAT_VEC3, gl.GL_FLOAT_VEC4,
                         gl.GL_INT, gl.GL_BOOL,
                         gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3,
                         gl.GL_FLOAT_MAT4, gl.GL_SAMPLER_2D,
                         gl.GL_SAMPLER_CUBE]:
            raise ValueError("Unknown variable type")

        # Name of this variable in the program
        self._name = name

        # GL type and size (i.e. size of the vector)
        self._gtype = gtype
        self._size, _, self._dtype = gl_typeinfo[self._gtype]

        # CPU data
        self._data = None

        # Location of the variable in the program slots
        self._loc = None

        # Whether an upload is required
        self._dirty = False

        # To suppress warnings
        self._show_warning_notset = True

    def invalidate(self):
        """ Set dirty flag, to force setting the variable on the Program
        object. """
        self._dirty = True

    @property
    def name(self):
        """ The name of the variable. """
        return self._name

    @property
    def gtype(self):
        """ The type of the underlying variable (as a GL constant). """
        return self._gtype

    @property
    def dtype(self):
        """ The type of the underlying variable (as a np dtype). """
        return self._dtype

    @property
    def size(self):
        """ The size of the variable (i.e. size of the vector in GLSL). """
        return self._size

    @property
    def active(self):
        """ Whether this variable is active in the program. """
        return self._loc is not None

    @property
    def data(self):
        """ The data for this variable (ndarray, VertexBuffer or Texture). """
        return self._data


# ----------------------------------------------------------- Uniform class ---
class Uniform(Variable):

    """ A Uniform represents a program uniform variable. """

    # NOTE: Variable, Uniform, Attribute are FRIENDS of Program,
    # and Program manimpulates the private attributes of these objects.

    _ufunctions = {
        gl.GL_FLOAT: (gl.glUniform1fv, 1),
        gl.GL_FLOAT_VEC2: (gl.glUniform2fv, 2),
        gl.GL_FLOAT_VEC3: (gl.glUniform3fv, 3),
        gl.GL_FLOAT_VEC4: (gl.glUniform4fv, 4),
        gl.GL_INT: (gl.glUniform1iv, 1),
        gl.GL_INT_VEC2: (gl.glUniform2iv, 2),
        gl.GL_INT_VEC3: (gl.glUniform3iv, 3),
        gl.GL_INT_VEC4: (gl.glUniform4iv, 4),
        gl.GL_BOOL: (gl.glUniform1iv, 1),
        gl.GL_BOOL_VEC2: (gl.glUniform2iv, 2),
        gl.GL_BOOL_VEC3: (gl.glUniform3iv, 3),
        gl.GL_BOOL_VEC4: (gl.glUniform4iv, 4),
        gl.GL_FLOAT_MAT2: (gl.glUniformMatrix2fv, 4),
        gl.GL_FLOAT_MAT3: (gl.glUniformMatrix3fv, 9),
        gl.GL_FLOAT_MAT4: (gl.glUniformMatrix4fv, 16),
        gl.GL_SAMPLER_2D: (gl.glUniform1i, 1),
        gl.GL_SAMPLER_CUBE: (gl.glUniform1i, 1),
        gl.ext.GL_SAMPLER_3D: (gl.glUniform1i, 1),
    }

    def __init__(self, name, gtype):
        Variable.__init__(self, name, gtype)

        # Get ufunc
        self._ufunction, self._numel = Uniform._ufunctions[self._gtype]

        # For textures:
        self._texture_unit = -1  # Set by Program
        self._textureClass = {
            gl.GL_SAMPLER_2D: Texture2D,
            gl.GL_SAMPLER_CUBE: TextureCubeMap,
            gl.ext.GL_SAMPLER_3D: Texture3D,
        }.get(
            gtype,
            None)

    @property
    def texture_unit(self):
        """ The texture unit (only valid if this uniform is a sampler/texture.
        """
        return self._texture_unit

    def set_data(self, data):
        """ Set data for this uniform. Data can be anything that can be
        conveted to a numpy array. If the uniform is a sampler, a Texture
        object is required.
        """

        if self._gtype in (gl.GL_SAMPLER_2D, gl.GL_SAMPLER_CUBE,
                           gl.ext.GL_SAMPLER_3D):
            # Textures need special handling
            if isinstance(data, Texture):
                self._data = data
            else:
                raise ValueError(
                    'Expected a Texture for uniform %s.' %
                    self.name)
        else:
            # Try to put it inside the array
            if self._data is None:
                size, _, dtype = gl_typeinfo[self._gtype]
                self._data = np.zeros(size, dtype)
            try:
                if not isinstance(data, np.ndarray):
                    data = np.array(data)
                self._data[...] = data.ravel()
            except ValueError:
                raise ValueError(
                    "Wrong data format for uniform %s" %
                    self.name)

        # Mark variable as dirty
        self._dirty = True

    def upload(self, program):
        """ Actual upload of data to GPU memory """

        # If there is not data, there is no point in uploading
        if self._data is None:
            if self._show_warning_notset:
                logger.warn("Value for uniform '%s' is not set." % self.name)
                self._show_warning_notset = False
            return

        # Check active status (mandatory)
        if self._loc is None:
            raise VariableError("Uniform is not active")

        #  WARNING : Uniform are supposed to keep their value between program
        #           activation/deactivation (from the GL documentation). It has
        #           been tested on some machines but if it is not the case on
        #           every machine, we can expect nasty bugs from these early
        #           returns

        # Matrices (need a transpose argument)
        if self._gtype in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3,
                           gl.GL_FLOAT_MAT4):
            if not self._dirty:
                return
            # OpenGL ES 2.0 does not support transpose
            transpose = False
            self._ufunction(self._loc, 1, transpose, self._data)
            self._dirty = False

        # Textures (need to get texture count)
        elif self._gtype in (gl.GL_SAMPLER_2D, gl.GL_SAMPLER_CUBE):
            # Always enable texture
            texture = self.data
            unit = self.texture_unit
            gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
            program.activate_object(texture)
            # Upload uniform only of needed
            if not self._dirty:
                return
            gl.glUniform1i(self._loc, unit)

        # Regular uniform
        else:
            if not self._dirty:
                return
            self._ufunction(self._loc, 1, self._data)

        # Mark as uploaded
        self._dirty = False


# --------------------------------------------------------- Attribute class ---
class Attribute(Variable):

    """
    An Attribute represents a program attribute variable.
    """

    # NOTE: Variable, Uniform, Attribute are FRIENDS of Program,
    # and Program manimpulates the private attributes of these objects.

    _afunctions = {
        gl.GL_FLOAT: gl.glVertexAttrib1f,
        gl.GL_FLOAT_VEC2: gl.glVertexAttrib2f,
        gl.GL_FLOAT_VEC3: gl.glVertexAttrib3f,
        gl.GL_FLOAT_VEC4: gl.glVertexAttrib4f
    }

    def __init__(self, name, gtype):
        Variable.__init__(self, name, gtype)

        # Count number of vertices
        self._count = 0

        # Whether this attribure is generic
        self._generic = False

    @property
    def count(self):
        """ The number of vertices for this attribute.
        May be None for generic attributes. """
        if self._generic or self._data is None:
            return None
        else:
            return self._data.count

    def set_data(self, data):
        """ Set data for this attribute. """

        # No magic conversion to VertexBuffer here. If we want it, we
        # should do it in Program.__setitem__

        # Data is a tuple with size <= 4, we assume this designates a generate
        # vertex attribute.
        if (isinstance(data, (float, int)) or
                (isinstance(data, (tuple, list)) and
                 len(data) in [1, 2, 3, 4])):
            # Get dtype, should be float32 for ES 2.0, see issue #9
            _, _, dtype = gl_typeinfo[self._gtype]
            if dtype != np.float32:
                logger.warn('Warning: OpenGL ES 2.0 only supports '
                            'float attributes.')
            # Let numpy convert the data for us
            self._data = np.array(data, dtype=dtype)
            self._data.shape = self._data.size,
            # Set generic and afunc
            self._generic = True
            self._afunction = Attribute._afunctions[self._gtype]

        elif isinstance(data, (ClientVertexBuffer, VertexBuffer)):
            # Just store the Buffer
            self._data = data
            self._generic = False
        elif isinstance(data, np.ndarray):
            raise ValueError(
                'Cannot set attribute data using numpy arrays: ' +
                'use tuple, ClientVertexBuffer or VertexBuffer instead. ')
        else:
            raise ValueError('Wrong data for attribute.')

        # Mark variable as dirty
        self._dirty = True

    def upload(self, program):
        """ Actual upload of data to GPU memory  """

        # If there is not data, there is no point in uploading
        if self._data is None:
            if self._show_warning_notset:
                logger.warn("Value for attribute '%s' is not set." % self.name)
                self._show_warning_notset = False
            return

        # Check active status (mandatory)
        if self._loc is None:
            raise VariableError("Attribute is not active")

        # Note: It has been seen (on my (AK) machine) that attributes
        # are *not* local to the program object; the splitscreen example
        # is broken if we use the early exits here.

        # todo: instead of setting dirty to true, remove early exits
        # (leaving for now for testing on other machines)
        self._dirty = True

        # Generic vertex attribute (all vertices receive the same value)
        if self._generic:

            # Tell OpenGL to use the constant value
            gl.glDisableVertexAttribArray(self._loc)

            # Early exit
            if not self._dirty:
                return

            # Apply
            self._afunction(self._loc, *self._data)

        # Client side array
        elif isinstance(self._data, ClientVertexBuffer):

            # Tell OpenGL to use the array and not the glVertexAttrib* value
            gl.glEnableVertexAttribArray(self._loc)

            # Disable any VBO
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

            # Early exit (pointer to CPU-data is still known by Program)
            if not self._dirty:
                return

            # Get numpy array from its container
            data = self._data.data

            # Check attribute format against data format
            size, gtype, _ = gl_typeinfo[self._gtype]
            # if self._gtype != self._data._gtype:
            #    raise ValueError("Data not compatible with attribute type")
            offset = 0
            stride = self._data.stride

            # Apply (first disable any previous VertexBuffer)
            gl.glVertexAttribPointer(
                self._loc,
                size,
                gtype,
                False,
                stride,
                data)

        # Regular vertex buffer or vertex buffer view
        else:

            data = self._data
            # todo: check offset = -1?

            # Tell OpenGL to use the array and not the glVertexAttrib* value
            gl.glEnableVertexAttribArray(self._loc)

            # Enable the VBO
            program.activate_object(data)

            # Early exit
            if not self._dirty:
                return

            # Check attribute format against data format
            size, gtype, _ = gl_typeinfo[self._gtype]
            # if self._gtype != self._data._gtype:
            #    raise ValueError("Data not compatible with attribute type")
            offset = self._data.offset
            stride = self._data.stride

            #size, gtype, dtype = gl_typeinfo[self._gtype]
            # offset, stride = data._offset, data._stride  # view_params not on
            # VertexBuffer

            # Make offset a pointer, or it will be interpreted as a small array
            offset = ctypes.c_void_p(offset)

            # Apply
            gl.glVertexAttribPointer(
                self._loc,
                size,
                gtype,
                False,
                stride,
                offset)

        # Mark as uploaded
        self._dirty = False
        logger.debug('upload attribute %s to %s' % (self.name, self._loc))
