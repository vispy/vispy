# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of the Data class """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.oogl import GLObject
from vispy.oogl import VertexBuffer



# ------------------------------------------------------------ Data class ---
class Data(GLObject):
    """The Data class allows to encapsulate several vertex buffers at once

    Example
    -------

    data = Data(1000, [('a_position', np.float32,3),
                       ('a_color',    np.float32,4)])
    data['a_color'] = 0,0,0,1
    """

    def __init__(self, size, *args):
        """ Initialize Data into default state. """

        GLObject.__init__(self)
        self._data = {}

        for dtype in args:
            dtype = np.dtype(dtype)
            if not dtype.fields:
                raise TypeError('dtype must be structured type')

            array  = np.empty(size, dtype)
            buffer = VertexBuffer(array)
            for name in dtype.names:
                self._data[name] = array,buffer 

    @property
    def data(self):
        """ Return a dictionnay of all vertex buffers """

        return { name:buffer[name] for name,(array,buffer) in self._data.items()}


    def __setitem__(self, key, value):
        """ """

        if key not in self._data.keys():
            raise AttributeError('Unknown attribute')

        array, buffer = self._data[key]
        array[key][...] = value

        # We mark the base buffer for a full update
        buffer[key].set_data(array)


    def __getitem__(self, key):
        """ Return the underlying numpy array. """

        if key not in self._data.keys():
            raise AttributeError('Unknown attribute')

        array, buffer = self._data[key]
        # We mark the base buffer for a full update since we do not
        # control whether the array will be changed afterwards
        buffer.set_data(array)
        return array[key]


    def __call__(self, key):
        """ Return the underlying vertex buffer. """

        if key not in self._data.keys():
            raise AttributeError('Unknown attribute')

        array, buffer = self._data[key]
        return buffer[key]


    def keys(self):
        """ Return a list of known attributes. """

        return self._data.keys()




# -----------------------------------------------------------------------------
if __name__ == '__main__':

    data = Data(100, [ ('a_position', np.float32, 3),
                       ('a_color', np.float32, 4) ],
                     [ ('a_rot', np.float32, 4) ] )
    data['a_position'] = np.ones((100,3))
    data['a_color'][::2] = 0,0,0,1
    data['a_rot'][::2] = 0,0,0,1

    # Return the underlying numpy array
    print( type(data['a_color']) )

    # Return the underlying vertex buffer
    print( type(data('a_color')) )
    
    # We could then use
    # program.attach(data)

    print( data.data )
