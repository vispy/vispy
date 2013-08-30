# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of VertexBuffer, ClientBuffer and ElemenBuffer classes """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util import is_string
from vispy.oogl import GLObject
from vispy.oogl import ext_available



# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """The Buffer class is a raw interface to upload some data to the GPU.
    It is data agnostic and doesn't check any data type.

    Note that it is possible to only upload subdata to the GPU without ever
    uploading the full buffer. In such case, you have to first set the size of
    the buffer. Once the size is set, checks will be made as to not override the
    end of the buffer. If you need more space, set a new size first.
    """


    def __init__(self, target, data=None, base=None):
        """ Initialize buffer into default state. """

        GLObject.__init__(self)
        
        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object.")
        self._target = target
        
        # Bytesize of buffer in GPU memory
        self._bytesize = 0

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW
        
        # Set data
        self._pending_data = []
        if data is not None:
            if not isinstance(data, np.ndarray):
                raise ValueError("Data should be a numpy array.")
            self._set_bytesize(data.nbytes)
            self.set_data(data)

        # Pointer to the base buffer (if any)
        self._base = base


    def set_data(self, data, offset=0):
        """ Set data or subdata (deferred operations)  """

        # Check some size has been allocated
        if self._bytesize == 0:
            raise ValueError("Buffer size is null.")

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        count = data.nbytes

        # If the whole buffer is to be written, we clear any pending data
        # operations since this will be overwritten anyway.
        if count == self._bytesize:
            if offset == 0:
                self._pending_data = []
            else:
                raise ValueError("Data is too big for buffer.")

        # Check if we have enough space
        if (offset+count) > self._bytesize:
            raise ValueError("Offseted data is too big for buffer.")

        # Ok, we should be safe now
        self._pending_data.append( (data, count, offset) )
        self._need_update = True


    def _set_bytesize(self, bytesize):
        """ Set buffer bytesize (invalidates all pending operations) """

        self._pending_data = []
        self._bytesize = bytesize
        self._valid = False # This will force a reallocation


    def _create(self):
        """ Create buffer on GPU """

        if self._base:
            self._base._create()
            return

        if not self._handle:
            handle = gl.glGenBuffers(1)
            self._handle = handle

        # Check if size has been changed and allocate new size if necessary
        gl.glBindBuffer(self._target, self._handle)
        bytesize = gl.glGetBufferParameteriv(self._target, gl.GL_BUFFER_SIZE)
        if bytesize != self._bytesize:
            # This will only allocate the buffer on GPU
            # WARNING: we should check of this operation is ok
            gl.glBufferData(self._target, self._bytesize, None, self._usage)
            # debug
            # print("Creating a new buffer (%d) of %d bytes"
            #        % (self._handle,self._bytesize))
        gl.glBindBuffer(self._target, 0)
        self._valid = True            


    def _delete(self):
        """ Delete buffer from GPU """

        if self._handle and gl:
            gl.glDeleteBuffers(1 , [self._handle])
            self._handle = 0
            self._valid = False
    

    def _activate(self):
        """ Bind the buffer to some target """

        if self._base:
            self._base.activate()
        else:
            gl.glBindBuffer(self._target, self._handle)


    def _deactivate(self):
        """ Unbind the current bound buffer """

        if self._base:
            self._base.deactivate()
        else:
            gl.glBindBuffer(self._target, 0)


    def _update(self):
        """ Upload all pending data to GPU. """
        
        # Bind buffer now 
        gl.glBindBuffer(self._target, self._handle)

        # Upload data
        while self._pending_data:
            data, count, offset = self._pending_data.pop(0)

            # debug
            # print("Uploading %d bytes at offset %d to buffer (%d)"
            #        % (count, offset, self._handle))

            gl.glBufferSubData(self._target, offset, count, data)

        # Sanity measure    
        gl.glBindBuffer(self._target, 0)
        self._need_update = False




# ------------------------------------------------------ DataBuffer class ---
class DataBuffer(Buffer):
    """Data buffer allows to manipulate typed data.  """


    def __init__(self, data=None, dtype=None, count=0, base=None, offset=0, target=0):
        """ Initialize the buffer """

        Buffer.__init__(self, target, data, base=base)

        # Check if this buffer is a view of another buffer
        if base is not None:
            self._dtype     = dtype
            self._itemsize  = base._itemsize
            self._itemcount = base._itemcount
            self._bytesize  = base._bytesize
            self._offset    = offset

        # Check if dtype is a numpy dtype
        elif dtype is not None:
            dtype = np.dtype(dtype)
            if isinstance(dtype,np.dtype):
                if count == 0:
                    raise ValueError("Count error (cannot be 0).")
                self._dtype     = dtype
                self._itemsize  = self._dtype.itemsize
                self._itemcount = count
                self._bytesize  = self._itemsize * self._itemcount
                self._offset    = 0
            else:
                raise ValueError("Unknown data type.")

        # Check if data is a numpy array
        elif isinstance(data,np.ndarray):
            self._dtype     = data.dtype
            self._bytesize  = data.nbytes
            self._itemsize  = self._dtype.itemsize
            self._itemcount = data.size
            self._offset    = 0

        # We need at least one (data) or the others (dtype+count)
        else:
            raise ValueError("One of 'data' or 'dtype' must be specified.")


        # Compute gl type corresponding to dtype
        gltypes = { ('int8',1)    : gl.GL_BYTE,
                    ('uint8',1)   : gl.GL_UNSIGNED_BYTE,
                    ('int16', 1)  : gl.GL_SHORT,
                    ('uint16',1)  : gl.GL_UNSIGNED_SHORT,
                    ('uint32',1)  : gl.GL_UNSIGNED_INT,
                    ('float16',1) : gl.ext.GL_HALF_FLOAT,
                    ('float32',1) : gl.GL_FLOAT,
                    ('float32',2) : gl.GL_FLOAT_VEC2,
                    ('float32',3) : gl.GL_FLOAT_VEC3,
                    ('float32',4) : gl.GL_FLOAT_VEC4,
                    ('float32',(2,2)) : gl.GL_FLOAT_MAT2,
                    ('float32',9) : gl.GL_FLOAT_MAT3,
                    ('float32',(3,3)) : gl.GL_FLOAT_MAT3,
                    ('float32',16) : gl.GL_FLOAT_MAT4,
                    ('float32',(4,4)) : gl.GL_FLOAT_MAT4,
                    ('int32',1) : gl.GL_INT,
                    ('int32',2) : gl.GL_INT_VEC2,
                    ('int32',3) : gl.GL_INT_VEC3,
                    ('int32',4) : gl.GL_INT_VEC4,
                    ('bool',1) : gl.GL_BOOL,
                    ('bool',2) : gl.GL_BOOL_VEC2,
                    ('bool',3) : gl.GL_BOOL_VEC3,
                    ('bool',4) : gl.GL_BOOL_VEC4 }

        dtype = self._dtype
        if dtype.fields and len(dtype.fields) == 1:
            dtype = dtype[dtype.names[0]]
        cshape = dtype.shape
        if cshape not in ( (2,2), (3,3), (4,4) ):
            cshape = int(np.prod(cshape))
        ctype = dtype.base
        self._gtype = gltypes.get((str(ctype), cshape), None)



    @property
    def dtype(self):
        """Buffer data type. """
        return self._dtype


    @property
    def gtype(self):
        """Buffer gl data type. """
        return self._gtype


    @property
    def itemcount(self):
        """Buffer element count. """
        return self._itemcount


    @property
    def itemsize(self):
        """Buffer element size (in bytes). """
        return self._itemsize


    @property
    def bytesize(self):
        """Buffer size (in bytes) """
        return self._bytesize


    @property
    def offset(self):
        """Buffer offset (in bytes) relative to base. """
        return self._offset


    @property
    def base(self):
        """Buffer base if this buffer is a view on another buffer. """
        return self._dtype


    def __setitem__(self, key, data):
        """Set data (deferred operation) """

        # Is this buffer a view on another ?
        if self._base is not None:
            raise ValueError("Cannot set data on buffer views.")
        
        # Deal with slices that have None or negatives in them
        if isinstance(key, slice):
            start = key.start or 0
            if start < 0:
                start = self._itemsize + start
            step = key.step or 1
            assert step > 0
            stop = key.stop or self._itemsize
            if stop < 0:
                stop = self._itemsize + stop
        
        # Check ellipsis (... notation)
        if key == Ellipsis:
            offset = 0
            count  = data.nbytes
        # If key is not a slice
        elif not isinstance(key, slice) or step > 1:
            raise ValueError("Can only set contiguous block of data.")
        # Else we're happy
        else:
            offset = start * self._itemsize
            count  = (stop - start) * self._itemsize

        # Check we have the right amount of data
        if data.nbytes < count:
            raise ValueError("Not enough data.")
        elif data.nbytes > count:
            raise ValueError("Too much data.")

        # WARNINR: Do we check data type here or do we cast the data to the
        # same internal dtype ? This would make a silent copy of the data which
        # can be problematic in some cases.
        data = data.astype(self._dtype)
        self.set_data(data, offset=offset)


    def __getitem__(self, key):
        """ Create a view on this buffer. """

        if not is_string(key):
            raise ValueError("Can only get access to a named field")

        dtype = self._dtype[key]
        offset = self._dtype.fields[key][1]
        return self.__class__(dtype=dtype, base=self, offset=offset)


    def _get_gtype(self, dtype=None):
        """ Get component type and number from a numpy dtype. """

        if dtype is None:
            dtype = self._dtype

        if dtype.fields and len(dtype.fields) == 1:
            dtype = dtype[dtype.names[0]]

        bsize = int(np.prod(dtype.shape))
        btype = dtype.base

        return btype, bsize





# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(DataBuffer):
    """Vertex buffer allows to group set of vertices such they can be later used
    in a shader program.

    Example
    -------

    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    data = np.zeros(100, dtype=dtype)

    buffer = VertexBuffer(data)
    program = Program(...)

    program['position'] = buffer['position']
    program['texcoord'] = buffer['texcoord']
    program['color'] = buffer['color']
    ...
    """


    def __init__(self, data=None, dtype=None, count=0, base=None, offset=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, count=count,
                            base=base, offset = offset, target = gl.GL_ARRAY_BUFFER)

        # Check data type
        #  (only when base is None, else, it has been already checked)
        if base is not None:
            return

        if self._dtype.fields:
            dtypes = [self._dtype[name] for name in self._dtype.names]
        else:
            dtypes = [self._dtype]

        for dtype in dtypes:
            btype, bsize = self._get_gtype(dtype)
            # Check component type
            if str(btype) not in ('uint8','uint16','int16', 'float32','float16'):
                raise TypeError(
                    """A vertex buffer element component type should """
                    """be one of uint8, uint16, int16, float32 or float16.""")
            # Check component count
            if bsize > 4:
                raise TypeError(
                    "A vertex buffer element type should have at most 4 components. ")

                        

# ------------------------------------------------------ ElementBuffer class ---
class ElementBuffer(DataBuffer):
    """ElementBuffer allows to specify which element of a VertexBuffer are to be
    used in a shader program.

    Example
    -------

    indices = np.zeros(100, dtype=np.uint16)
    buffer = ElementBuffer(indices)
    program = Program(...)

    program.draw(gl.GL_TRIANGLES, indices)
    ...
    """
    
    def __init__(self, data=None, dtype=None, count=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, count=count,
                            target = gl.GL_ELEMENT_ARRAY_BUFFER)
        
        btype,bsize = self._get_gtype()

        # Check component type
        if str(btype) not in ('uint8', 'uint16', 'uint32'):
            raise TypeError("An element buffer data type should be one of " +
                            "uint8, uint16 or uint32. ")
        # Check component count
        if bsize > 1:
            raise TypeError("An element buffer data should be contiguous.")



# ------------------------------------------------------ ClientBuffer class ---
class ClientBuffer(DataBuffer):
    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer. It merely serves as
    passing direct data during a drawing operations.
    
    Note this kind of buffer is highly inefficient since data is uploaded at
    each drawing operations.
    """

    def __init__(self, data):
        """ Initialize the buffer. """

        DataBuffer.__init__(self,data=data, target=gl.GL_ARRAY_BUFFER)

        self._value       = True
        self._need_update = True
        self._data        = data

        self._dtype     = data.dtype
        self._itemsize  = data.dtype.itemsize
        self._itemcount = data.size
        self._bytesize  = data.size * data.dtype.itemsize
        self._offset    = 0


    @property
    def data(self):
        """Buffer data. """
        return self._data

    def __getitem__(self, key):        pass
    def __setitem__(self, key, data):  pass
    def _create(self):                 pass
    def _delete(self):                 pass
    def _activate(self):               pass
    def _deactivate(self):             pass
    def _update(self):                 pass



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import OpenGL.GLUT as glut


    V = VertexBuffer(np.ones(100, np.float32))
    print("Offset:",     V.offset)
    print("Itemsize:",   V.itemsize)
    print("Itemcount",   V.itemcount)
    print("Data gtype %r" % V.gtype)
    print()


    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    data = np.zeros(100, dtype=dtype)
    indices = np.zeros(100, dtype=np.uint16)

    V = VertexBuffer(data)
    V_position = V['position']
    V_texcoord = V['texcoord']
    V_color    = V['color']

    for P in (V_position, V_texcoord, V_color):
        print("Offset:",    P.offset)
        print("Itemsize:",  P.itemsize)
        print("Itemcount",  P.itemcount)
        print("Data gtype %r" % P.gtype)
        print()

    V[10:20] = data[10:20]
    V[...] = data
    print( len(V._pending_data))
    #V[10:20] = data[10:19]
    #V[10:20] = data[10:21]

    I = ElementBuffer(indices)
    print("Offset:",    I.offset)
    print("Itemsize:",  I.itemsize)
    print("Itemcount",  I.itemcount)
    print("Data gtype %r" % I.gtype)
    print()
    


    def display():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        glut.glutSwapBuffers()

    def reshape(width,height):
        gl.glViewport(0, 0, width, height)

    def keyboard( key, x, y ):
        if key == '\033': sys.exit( )

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutCreateWindow('Shader test')
    glut.glutReshapeWindow(512,512)
    glut.glutDisplayFunc(display)
    glut.glutReshapeFunc(reshape)
    glut.glutKeyboardFunc(keyboard )

    V.activate()
    V.deactivate()
