# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
A collection is a container for several (optionally indexed) objects having
the same vertex structure (vtype) and same uniforms type (utype). A collection
allows to manipulate objects individually and each object can have its own set
of uniforms provided they are a combination of floats.
"""

from __future__ import division

import math
import numpy as np
from ...gloo import Texture2D, VertexBuffer, IndexBuffer
from . util import dtype_reduce
from . array_list import ArrayList


def next_power_of_2(n):
    """ Return next power of 2 greater than or equal to n """
    n -= 1  # greater than OR EQUAL TO n
    shift = 1
    while (n + 1) & n:  # n+1 is not a power of 2 yet
        n |= n >> shift
        shift *= 2
    return max(4, n + 1)


class Item(object):

    """
    An item represent an object within a collection and is created on demand
    when accessing a specific object of the collection.
    """

    def __init__(self, parent, key, vertices, indices, uniforms):
        """
        Create an item from an existing collection.

        Parameters
        ----------

        parent : Collection
            Collection this item belongs to

        key : int
            Collection index of this item

        vertices: array-like
            Vertices of the item

        indices: array-like
            Indices of the item

        uniforms: array-like
            Uniform parameters of the item
        """

        self._parent = parent
        self._key = key
        self._vertices = vertices
        self._indices = indices
        self._uniforms = uniforms

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, data):
        self._vertices[...] = np.array(data)

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, data):
        if self._indices is None:
            raise ValueError("Item has no indices")
        start = self._parent.vertices._items[self._key][0]
        self._indices[...] = np.array(data) + start

    @property
    def uniforms(self):
        return self._uniforms

    @uniforms.setter
    def uniforms(self, data):
        if self._uniforms is None:
            raise ValueError("Item has no associated uniform")
        self._uniforms[...] = data

    def __getitem__(self, key):
        """ Get a specific uniforms value """

        if key in self._vertices.dtype.names:
            return self._vertices[key]
        elif key in self._uniforms.dtype.names:
            return self._uniforms[key]
        else:
            raise IndexError("Unknown key ('%s')" % key)

    def __setitem__(self, key, value):
        """ Set a specific uniforms value """

        if key in self._vertices.dtype.names:
            self._vertices[key] = value
        elif key in self._uniforms.dtype.names:
            self._uniforms[key] = value
        else:
            raise IndexError("Unknown key")

    def __str__(self):
        return "Item (%s, %s, %s)" % (self._vertices,
                                      self._indices,
                                      self._uniforms)


class BaseCollection(object):

    def __init__(self, vtype, utype=None, itype=None):

        # Vertices and type (mandatory)
        self._vertices_list = None
        self._vertices_buffer = None

        # Vertex indices and type (optional)
        self._indices_list = None
        self._indices_buffer = None

        # Uniforms and type (optional)
        self._uniforms_list = None
        self._uniforms_texture = None

        # Make sure types are np.dtype (or None)
        vtype = np.dtype(vtype) if vtype is not None else None
        itype = np.dtype(itype) if itype is not None else None
        utype = np.dtype(utype) if utype is not None else None

        # Vertices type (mandatory)
        # -------------------------
        if vtype.names is None:
            raise ValueError("vtype must be a structured dtype")

        # Indices type (optional)
        # -----------------------
        if itype is not None:
            if itype not in [np.uint8, np.uint16, np.uint32]:
                raise ValueError("itype must be unsigned integer or None")
            self._indices_list = ArrayList(dtype=itype)

        # No program yet
        self._programs = []

        # Need to update buffers & texture
        self._need_update = True

        # Uniforms type (optional)
        # -------------------------
        if utype is not None:

            if utype.names is None:
                raise ValueError("utype must be a structured dtype")

            # Convert types to lists (in case they were already dtypes) such
            # that we can append new fields
            vtype = eval(str(np.dtype(vtype)))
            # We add a uniform index to access uniform data
            vtype.append(('collection_index', np.float32))
            vtype = np.dtype(vtype)

            # Check utype is made of float32 only
            utype = eval(str(np.dtype(utype)))
            r_utype = dtype_reduce(utype)
            if type(r_utype[0]) is not str or r_utype[2] != 'float32':
                raise RuntimeError("utype cannot be reduced to float32 only")

            # Make utype divisible by 4
            # count = ((r_utype[1]-1)//4+1)*4

            # Make utype a power of two
            count = next_power_of_2(r_utype[1])
            if (count - r_utype[1]) > 0:
                utype.append(('__unused__', np.float32, count - r_utype[1]))

            self._uniforms_list = ArrayList(dtype=utype)
            self._uniforms_float_count = count

            # Reserve some space in texture such that we have
            # at least one full line
            shape = self._compute_texture_shape(1)
            self._uniforms_list.reserve(shape[1] / (count / 4))

        # Last since utype may add a new field in vtype (collecion_index)
        self._vertices_list = ArrayList(dtype=vtype)

        # Record all types
        self._vtype = np.dtype(vtype)
        self._itype = np.dtype(itype) if itype is not None else None
        self._utype = np.dtype(utype) if utype is not None else None

    def __len__(self):
        """ x.__len__() <==> len(x) """

        return len(self._vertices_list)

    @property
    def vtype(self):
        """ Vertices dtype """

        return self._vtype

    @property
    def itype(self):
        """ Indices dtype """

        return self._itype

    @property
    def utype(self):
        """ Uniforms dtype """

        return self._utype

    def append(self, vertices, uniforms=None, indices=None, itemsize=None):
        """
        Parameters
        ----------

        vertices : numpy array
            An array whose dtype is compatible with self.vdtype

        uniforms: numpy array
            An array whose dtype is compatible with self.utype

        indices : numpy array
            An array whose dtype is compatible with self.idtype
            All index values must be between 0 and len(vertices)

        itemsize: int, tuple or 1-D array
            If `itemsize is an integer, N, the array will be divided
            into elements of size N. If such partition is not possible,
            an error is raised.

            If `itemsize` is 1-D array, the array will be divided into
            elements whose succesive sizes will be picked from itemsize.
            If the sum of itemsize values is different from array size,
            an error is raised.
        """

        # Vertices
        # -----------------------------
        vertices = np.array(vertices).astype(self.vtype).ravel()
        vsize = self._vertices_list.size

        # No itemsize given
        # -----------------
        if itemsize is None:
            index = 0
            count = 1

        # Uniform itemsize (int)
        # ----------------------
        elif isinstance(itemsize, int):
            count = len(vertices) / itemsize
            index = np.repeat(np.arange(count), itemsize)

        # Individual itemsize (array)
        # ---------------------------
        elif isinstance(itemsize, (np.ndarray, list)):
            count = len(itemsize)
            index = np.repeat(np.arange(count), itemsize)
        else:
            raise ValueError("Itemsize not understood")

        if self.utype:
            vertices["collection_index"] = index + len(self)
        self._vertices_list.append(vertices, itemsize)

        # Indices
        # -----------------------------
        if self.itype is not None:
            # No indices given (-> automatic generation)
            if indices is None:
                indices = vsize + np.arange(len(vertices))
                self._indices_list.append(indices, itemsize)

            # Indices given
            # FIXME: variables indices (list of list or ArrayList)
            else:
                if itemsize is None:
                    I = np.array(indices) + vsize
                elif isinstance(itemsize, int):
                    I = vsize + (np.tile(indices, count) +
                                 itemsize * np.repeat(np.arange(count), len(indices)))  # noqa
                else:
                    raise ValueError("Indices not compatible with items")
                self._indices_list.append(I, len(indices))

        # Uniforms
        # -----------------------------
        if self.utype:
            if uniforms is None:
                uniforms = np.zeros(count, dtype=self.utype)
            else:
                uniforms = np.array(uniforms).astype(self.utype).ravel()
            self._uniforms_list.append(uniforms, itemsize=1)

        self._need_update = True

    def __delitem__(self, index):
        """ x.__delitem__(y) <==> del x[y] """

        # Deleting one item
        if isinstance(index, int):
            if index < 0:
                index += len(self)
            if index < 0 or index > len(self):
                raise IndexError("Collection deletion index out of range")
            istart, istop = index, index + 1
        # Deleting several items
        elif isinstance(index, slice):
            istart, istop, _ = index.indices(len(self))
            if istart > istop:
                istart, istop = istop, istart
            if istart == istop:
                return
        # Deleting everything
        elif index is Ellipsis:
            istart, istop = 0, len(self)
        # Error
        else:
            raise TypeError("Collection deletion indices must be integers")

        vsize = len(self._vertices_list[index])
        if self.itype is not None:
            del self._indices_list[index]
            self._indices_list[index:] -= vsize

        if self.utype:
            self._vertices_list[index:]["collection_index"] -= istop - istart
        del self._vertices_list[index]

        if self.utype is not None:
            del self._uniforms_list[index]

        self._need_update = True

    def __getitem__(self, key):
        """ """

        # WARNING
        # Here we want to make sure to use buffers and texture (instead of
        # lists) since only them are aware of any external modification.
        if self._need_update:
            self._update()

        V = self._vertices_buffer
        I = None
        U = None
        if self._indices_list is not None:
            I = self._indices_buffer
        if self._uniforms_list is not None:
            U = self._uniforms_texture.data.ravel().view(self.utype)

        # Getting a whole field
        if isinstance(key, str):
            # Getting a named field from vertices
            if key in V.dtype.names:
                return V[key]
            # Getting a named field from uniforms
            elif U is not None and key in U.dtype.names:
                # Careful, U is the whole texture that can be bigger than list
                # return U[key]
                return U[key][:len(self._uniforms_list)]
            else:
                raise IndexError("Unknown field name ('%s')" % key)

        # Getting individual item
        elif isinstance(key, int):
            vstart, vend = self._vertices_list._items[key]
            vertices = V[vstart:vend]
            indices = None
            uniforms = None
            if I is not None:
                istart, iend = self._indices_list._items[key]
                indices = I[istart:iend]

            if U is not None:
                ustart, uend = self._uniforms_list._items[key]
                uniforms = U[ustart:uend]

            return Item(self, key, vertices, indices, uniforms)

        # Error
        else:
            raise IndexError("Cannot get more than one item at once")

    def __setitem__(self, key, data):
        """ x.__setitem__(i, y) <==> x[i]=y """

        # if len(self._programs):
        # found = False
        # for program in self._programs:
        #     if key in program.hooks:
        #         program[key] = data
        #         found = True
        # if found: return

        # WARNING
        # Here we want to make sure to use buffers and texture (instead of
        # lists) since only them are aware of any external modification.
        if self._need_update:
            self._update()

        V = self._vertices_buffer
        I = None
        U = None
        if self._indices_list is not None:
            I = self._indices_buffer  # noqa
        if self._uniforms_list is not None:
            U = self._uniforms_texture.data.ravel().view(self.utype)

        # Setting a whole field
        if isinstance(key, str):
            # Setting a named field in vertices
            if key in self.vtype.names:
                V[key] = data
            # Setting a named field in uniforms
            elif self.utype and key in self.utype.names:
                # Careful, U is the whole texture that can be bigger than list
                # U[key] = data
                U[key][:len(self._uniforms_list)] = data
            else:
                raise IndexError("Unknown field name ('%s')" % key)

        # # Setting individual item
        # elif isinstance(key, int):
        #     #vstart, vend = self._vertices_list._items[key]
        #     #istart, iend = self._indices_list._items[key]
        #     #ustart, uend = self._uniforms_list._items[key]
        #     vertices, indices, uniforms = data
        #     del self[key]
        #     self.insert(key, vertices, indices, uniforms)

        else:
            raise IndexError("Cannot set more than one item")

    def _compute_texture_shape(self, size=1):
        """ Compute uniform texture shape """

        # We should use this line but we may not have a GL context yet
        # linesize = gl.glGetInteger(gl.GL_MAX_TEXTURE_SIZE)
        linesize = 1024
        count = self._uniforms_float_count
        cols = 4 * linesize // int(count)
        rows = max(1, int(math.ceil(size / float(cols))))
        shape = rows, cols * (count // 4), count
        self._ushape = shape
        return shape

    def _update(self):
        """ Update vertex buffers & texture """

        if self._vertices_buffer is not None:
            self._vertices_buffer.delete()
        self._vertices_buffer = VertexBuffer(self._vertices_list.data)

        if self.itype is not None:
            if self._indices_buffer is not None:
                self._indices_buffer.delete()
            self._indices_buffer = IndexBuffer(self._indices_list.data)

        if self.utype is not None:
            if self._uniforms_texture is not None:
                self._uniforms_texture.delete()

            # We take the whole array (_data), not the data one
            texture = self._uniforms_list._data.view(np.float32)
            size = len(texture) / self._uniforms_float_count
            shape = self._compute_texture_shape(size)

            # shape[2] = float count is only used in vertex shader code
            texture = texture.reshape(shape[0], shape[1], 4)
            self._uniforms_texture = Texture2D(texture)
            self._uniforms_texture.data = texture
            self._uniforms_texture.interpolation = 'nearest'

        if len(self._programs):
            for program in self._programs:
                program.bind(self._vertices_buffer)
                if self._uniforms_list is not None:
                    program["uniforms"] = self._uniforms_texture
                    program["uniforms_shape"] = self._ushape
