# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of VertexBuffer, ClientBuffer and ElemenBuffer classes. """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util import is_string
from vispy.oogl import GLObject
from vispy.oogl import ext_available

# WARNING:
# We have to be very careful with VertexBuffer.
# Let's consider the following array:
#
# P = np.zeros(100, [ ('position', 'f4', 3),
#                      ('color',   'f4', 4),
#                      ('size',    'f4', 1)] )
#
# P.dtype itemsize is (3+4+1)*4 (float32)
#
# Now, if we create a VertexBuffer on position only:
#
# V = VertexBuffer(P['position'])
#
# The underlying data is not contiguous and we cannot use glBufferSubData to
# update the data into GPU memory. This means we need a local copy of the data
# to be able to upload it (PyOpenGL will handle that). We need also to find the
# stride of the buffer into GPU memory, not on CPU memory.

# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """The Buffer class is a raw interface to upload some data to the GPU.
    It is data agnostic and doesn't check any data type.

    Note that it is possible to only upload subdata to the GPU without ever
    uploading the full buffer. In such case, you have to first set the size of
    the buffer. Once the size is set, checks will be made as to not override the
    end of the buffer. If you need more space, set a new size first.
    """


    def __init__(self, target, data=None):
        """ Initialize buffer into default state. """

        GLObject.__init__(self)
        
        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object.")
        self._target = target

        # Number of elements in the buffer
        self._size = 0

        # Total bytes consumed by the elements of the buffer
        self._nbytes = 0

        # Byte number separating elements
        self._stride = 1

        # Indicate if a resize has been requested
        self._need_resize = True

        self._base = self

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW

        # Set data
        self._pending_data = []
        if data is not None:
            if not isinstance(data, np.ndarray):
                raise ValueError("Data should be a numpy array.")
            self.set_size(data.size)
            self.set_data(data)


    def set_data(self, data, offset=0, allow_resize=True):
        """ Set data or subdata (deferred operations)  """

        # Check some size has been allocated
        if self._nbytes == 0:
            raise ValueError("Buffer size is null.")

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        nbytes = data.nbytes

        # If the whole buffer is to be written, we clear any pending data
        # operations since this will be overwritten anyway.
        if nbytes == self._nbytes:
            if offset == 0:
                self._pending_data = []
            else:
                raise ValueError("Data is too big for buffer.")

        # Check if we have enough space when offset > 0
        if offset and (offset+nbytes) > self._nbytes:
            raise ValueError("Offseted data is too big for buffer.")
        
        # Resize if data too big
        elif nbytes > self._nbytes:
            if allow_resize:
                self.set_size(nbytes/self._stride)
            else:
                raise ValueError("Data is too big for buffer.")

        # Ok, we should be safe now
        #if data.base is data or self._base is self:
        self._pending_data.append( (data, nbytes, offset) )
        #else:
        #self._pending_data.append( (data.copy(), nbytes, offset) )
        self._need_update = True


    def set_subdata(self, data, offset=0):
        """ Set subdata (deferred operations, no resize allowed). """

        self.set_data(data,offset,allow_resize=False)


    def set_size(self, size):
        """ Set buffer size (invalidates all pending operations). """

        if size == self._size:
            return

        self._pending_data = []
        self._size = int(size)
        self._nbytes = int(size * self.stride)
        # This indicate to allocate buffer on GPU when possible
        self._need_resize = True


    @property
    def size(self):
        """ Number of elements in the array. """
        return self._size


    @property
    def stride(self):
        """Buffer element size (in bytes). """
        return self._stride


    @property
    def nbytes(self):
        """Buffer size (in bytes). """
        return self._nbytes


    @property
    def offset(self):
        """Buffer offset (in bytes) relative to base. """
        return self._offset

    @property
    def handle(self):
        """ Return a handle on the base buffer """

        return self._handle


    def _create(self):
        """ Create buffer on GPU """
        
        if not self._handle:
            self._handle = gl.glGenBuffers(1)
    
    def _delete(self):
        """ Delete buffer from GPU """
        
        gl.glDeleteBuffers(1 , [self._handle])
    
    
    def _activate(self):
        """ Bind the buffer to some target """
        
        gl.glBindBuffer(self._target, self._handle)


    def _deactivate(self):
        """ Unbind the current bound buffer """

        gl.glBindBuffer(self._target, 0)


    def _update(self):
        """ Upload all pending data to GPU. """

        # Bind buffer now 
        gl.glBindBuffer(self._target, self._handle)
       
        # Allocate new size if necessary
        if self._need_resize:
            # This will only allocate the buffer on GPU
            # WARNING: we should check if this operation is ok
            gl.glBufferData(self._target, self._nbytes, None, self._usage)
            # debug
            #print("Creating a new buffer (%d) of %d bytes"
            #        % (self._handle,self._nbytes))
            self._need_resize = False
            
        # Upload data
        while self._pending_data:
            data, size, offset = self._pending_data.pop(0)
            # debug
            # print("Uploading %d bytes at offset %d to buffer (%d)"
            #        % (size, offset, self._handle))
            gl.glBufferSubData(self._target, offset, size, data)





# ------------------------------------------------------ DataBuffer class ---
class DataBuffer(Buffer):
    """Data buffer allows to manipulate typed data.  """


    def __init__(self, data=None, dtype=None, size=0, offset=0, target=0):
        """ Initialize the buffer """

        Buffer.__init__(self, target)

        # Computed shape (for simple buffer or view)
        self._shape = None

        # Check if dtype is a numpy dtype
        if dtype is not None:
            dtype = np.dtype(dtype)
            if isinstance(dtype,np.dtype):
                if size == 0:
                    raise ValueError("Size error (cannot be 0).")
                self._dtype    = dtype
                self._stride   = self._dtype.itemsize
                self._size     = size
                self._nbytes   = self._stride * self._size
                self._offset   = 0
                self._shape    = (size,1)

                # Compute internal shape as (x,y) and base dtype
                dtype = self._dtype
                shape = [size,]
                if dtype.fields:
                    if len(dtype.fields) == 1:
                        shape.extend( [np.prod(dtype[0].shape)] )
                else:
                    self._dtype = dtype.base
                    shape.extend( dtype.shape)
                if len(shape) == 1:
                    shape = (shape[0],1)
                elif len(shape) > 2:
                    shape = (np.prod(shape[:-1]),shape[:-1])
                self._shape = tuple(shape)

            else:
                raise ValueError("Unknown data type.")

        # Check if data is a numpy array
        elif isinstance(data,np.ndarray):
            # If data is a structure array with a unique field
            # we get this unique field as data
            if data.dtype.fields and len(data.dtype.fields) == 1:
                data = data[data.dtype.names[0]]
                
            self._dtype   = data.dtype
            self._nbytes  = data.nbytes
            self._stride  = self._dtype.itemsize
            self._size    = data.size
            self._offset  = 0

            # Compute internal shape as (x,y) and base dtype
            dtype = data.dtype
            shape = list(data.shape) or [1]

            if dtype.fields:
                if len(dtype.fields) == 1:
                    shape.extend( [np.prod(dtype[0].shape)] )
            else:
                self._dtype = dtype.base
                shape.extend( dtype.shape)
            if len(shape) == 1:
                shape = (shape[0],1)
            elif len(shape) > 2:
                shape = (np.prod(shape[:-1]),shape[:-1])
            self._shape = shape

            # Data is a view on a structured array (no contiguous data) We know
            # that when setting data we'll have to make a local copy so we need
            # to compute the stride relative to GPU layout and not use the
            # stride of the original array.
            if data.base is not data:
                self._stride = self._dtype.itemsize * shape[-1]
                self._size   = shape[0]

        # We need at least one (data) or the others (dtype+size)
        else:
            raise ValueError("One of 'data' or 'dtype' must be specified.")

        # Set data only once properly initialized
        if data is not None:
            self.set_data(data)


    @property
    def dtype(self):
        """Buffer data type. """
        return self._dtype


    @property
    def base(self):
        """Buffer base if this buffer is a view on another buffer. """
        return self._base


    def __setitem__(self, key, data):
        """Set data (deferred operation) """

        # Deal with slices that have None or negatives in them
        if isinstance(key, slice):
            start = key.start or 0
            if start < 0:
                start = self._stride + start
            step = key.step or 1
            assert step > 0
            stop = key.stop or self._stride
            if stop < 0:
                stop = self._stride + stop
        
        # Check ellipsis (... notation)
        if key == Ellipsis:
            offset = 0
            nbytes = data.nbytes
        # If key is not a slice
        elif not isinstance(key, slice) or step > 1:
            raise ValueError("Can only set contiguous block of data.")
        # Else we're happy
        else:
            offset = start * self._stride
            nbytes = (stop - start) * self._stride

        # Check we have the right amount of data
        if data.nbytes < nbytes:
            raise ValueError("Not enough data.")
        elif data.nbytes > nbytes:
            raise ValueError("Too much data.")

        # WARNING: Do we check data type here or do we cast the data to the
        # same internal dtype ? This would make a silent copy of the data which
        # can be problematic in some cases.
        if data.dtype != self._dtype:
            data = data.astype(self._dtype)  # astype() always makes a copy
        self.set_data(data, offset=offset)


    def __getitem__(self, key):
        """ Create a view on this buffer. """

        if not is_string(key):
            raise ValueError("Can only get access to a named field")

        dtype = self._dtype[key]
        size = self._size 
        offset = self._dtype.fields[key][1]

        return VertexBufferView(dtype=dtype, size=size, base=self, offset=offset)





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


    def __init__(self, data=None, dtype=None, size=0, offset=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size,
                            offset = offset, target = gl.GL_ARRAY_BUFFER)

        # Check base type
        # For structured dtype, we let view check individual dtypes
        if self._dtype.fields and len(self._dtype.fields) > 1:
            return

        
        basetype = None
        if self._dtype.fields:
            if len(self._dtype.fields) == 1:
                basetype = self._dtype[0].base
        else:
            basetype = self._dtype.base

        if basetype not in (np.uint8,np.int8,np.uint16,
                            np.int16,np.float32,np.float16):
            raise TypeError("Data type not allowed for this buffer")




# ------------------------------------------------------ VertexBuffer class ---
class VertexBufferView(VertexBuffer):
    """ A VertexBufferView is a view on another buffer

    See VerteBuffer for usage.
    """

    def __init__(self, dtype=None, size=0, base=None, offset=0):
        """ Initialize the view """
        
        VertexBuffer.__init__(self, dtype=dtype, size=size, offset=offset)
        self._base = base
        self._offset = offset
        self._stride = base.stride


    def set_size(self, size):
        """ Set buffer base size (invalidates all pending operations) """
        self._base.set_size(size)


    @property
    def handle(self):
        """ Handle on base buffer. """
        self._handle = self._base._handle
        return self._handle


    @property
    def dtype(self):
        """ Element type. """
        return self._dtype


    @property
    def size(self):
        """ Size in number of elements. """
        return self._base.size


    @property
    def stride(self):
        """ Byte number separating two elements. """
        return self._base.stride


    @property
    def offset(self):
        """ Byte offset relative to base. """
        return self._offset


    @property
    def base(self):
        """ Vertex buffer base of this view. """
        return self._base


    def _create(self):
        """ Create buffer on GPU """
        self._base._create()
        self._handle = self._base._handle
    
    
    def _delete(self):
        """ Delete base buffer from GPU. """
        self._base.delete()
    
    
    def _activate(self):
        """ Bind the base buffer to some target """
        self._base.activate()


    def _deactivate(self):
        """ Unbind the base buffer """
        self._base.deactivate()


    def _update(self):
        """ Update base buffer. """

        self._base._update()
        self._need_update = False



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
    
    def __init__(self, data=None, dtype=None, size=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size,
                            target = gl.GL_ELEMENT_ARRAY_BUFFER)

        # Check dtype and shape

        if self._dtype not in (np.uint8,np.uint16,np.uint32):
            raise TypeError("Data type not allowed for this buffer")

        if self._shape[1] != 1:
            raise TypeError("Only contiguous data allowed for this buffer")




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

        self._dtype  = data.dtype
        self._stride = data.dtype.itemsize
        self._size   = data.size
        self._nbytes = data.size * data.dtype.itemsize
        self._offset = 0


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
    import sys
    import OpenGL.GLUT as glut

    VertexBuffer(np.array(100, dtype=np.float32))

    data = np.zeros(100, [ ('a', np.float32, 1),
                           ('b', np.float32, 2),
                           ('c', np.float32, 3) ] )
    buffer = VertexBuffer(data)
    print( buffer['a']._shape )
    print( buffer['a']._dtype )
    print( buffer['b']._shape )
    print( buffer['b']._dtype )
    print( buffer['c']._shape )
    print( buffer['c']._dtype )
    sys.exit()


    data = np.zeros(100, [('index', np.uint32,2)])
    buffer = ElementBuffer(data=data)
    print( buffer._shape )
    sys.exit()


    V = VertexBuffer(size=100, dtype=np.float32)
    print("Size",     V.size)
    print("Offset:",  V.offset)
    print("Stride:",  V.stride)
    print()

    V.set_data(np.ones(200, np.float32))
    print("Size",     V.size)
    print("Offset:",  V.offset)
    print("Stride:",  V.stride)
    print()



    V = VertexBuffer(np.ones(100, np.float32))
    print("Size",     V.size)
    print("Offset:",  V.offset)
    print("Stride:",  V.stride)
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
        print("Size",     P.size)
        print("Offset:",  P.offset)
        print("Stride:",  P.stride)
        print()

    V[10:20] = data[10:20]
    V[...] = data
    print( len(V._pending_data))
    #V[10:20] = data[10:19]
    #V[10:20] = data[10:21]

    I = ElementBuffer(indices)
    print("Size",     I.size)
    print("Offset:",  I.offset)
    print("Stride:",  I.stride)

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
    V['position'].activate()
    V['position'].deactivate()
    V.deactivate()
