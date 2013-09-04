# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of VertexBuffer, ElemenBuffer and client buffer classes. """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util import is_string
from vispy.oogl import GLObject
from vispy.oogl import ext_available

# Removed from Buffer:
# - self._size
# - self._stride
# - self._base


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
        
        # Total bytes consumed by the elements of the buffer
        self._nbytes = 0
        
        # Indicate if a resize has been requested
        self._need_resize = False
        
        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW

        # Set data
        self._pending_data = []
        if data is not None:
            self.set_data(data)
    
    
    def set_nbytes(self, nbytes):
        """ Set how many bytes are available for the buffer. 
        """
        nbytes = int(nbytes)
        
        # Set new bytes
        if self._nbytes != nbytes:
            self._nbytes = int(nbytes)
            self._need_resize = True
        
        # Clear pending subdata
        self._pending_data = []
    
    
    def set_data(self, data):
        """ Set the bytes data. For now, this only accepts a numpy array.
        But the data is not checked for dtype or shape.
        """
        
        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Set shape if necessary
        self.set_nbytes(data.nbytes)
        
        # Set pending!
        nbytes = data.nbytes
        self._pending_data.append( (data, nbytes, 0) )
        self._need_update = True
    
    
    def set_subdata(self, offset, data):
        """ Set subdata using an integer offset.
        """
        
        # Check some size has been allocated
        if not self._nbytes:
            raise ValueError("Cannot set subdata if there is no space allocated.")
            
        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Get offset and nbytes
        offset = int(offset)
        nbytes = data.nbytes
        
        # Check
        if (offset+nbytes) > self._nbytes:
            raise ValueError("Offseted data is too big for buffer.")
        
        # Set pending!
        self._pending_data.append( (data, nbytes, offset) )
        self._need_update = True
    
    
    @property
    def nbytes(self):
        """Buffer size (in bytes). """
        return self._nbytes


    @property
    def offset(self):
        """Buffer offset (in bytes) relative to base. """
        return self._offset
    
    
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
            data, nbytes, offset = self._pending_data.pop(0)
            # debug
            # print("Uploading %d bytes at offset %d to buffer (%d)"
            #        % (size, offset, self._handle))
            gl.glBufferSubData(self._target, offset, nbytes, data)





# ------------------------------------------------------ DataBuffer class ---
class DataBuffer(Buffer):
    """Data buffer allows to manipulate typed data.  """


    def __init__(self, data=None, dtype=None, target=None):
        """ Initialize the buffer """
        
        Buffer.__init__(self, target)
        
        # Computed shape (for simple buffer or view)
        self._shape = None
        
        # Byte number separating elements
        self._stride = 1
        
        # Flag
        self._nonrealbuffer_initialized = False
        
        # Set data
        if isinstance(data, np.ndarray):
            self.set_data(data)
        elif isinstance(data, (int, tuple)):
            self.set_shape(data, dtype)


    @property
    def dtype(self):
        """Buffer data type. """
        return self._dtype
    
    
    @property
    def shape(self):
        """ Get the shape of the underlying data. 
        """
        return self._shape
    
    
    @property
    def stride(self):
        """ Get the stride of the data, i.e. the number of bytes to move
        to the next element.
        """
        return self._stride
    
    
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
            start = 0
            nbytes = data.nbytes
        # If key is not a slice
        elif not isinstance(key, slice) or step > 1:
            raise ValueError("Can only set contiguous block of data.")
        # Else we're happy
        else:
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
        # Set
        self.set_subdata(start, data)
    
    
    def __getitem__(self, key):
        """ Create a view on this buffer. """
        
        if not is_string(key):
            raise ValueError("Can only get access to a named field")
        
        dtype = self._dtype[key].base
        shape = (self.shape[0],) + dtype.shape
        offset = self._dtype.fields[key][1]
        
        return VertexBufferView(shape, dtype, base=self, offset=offset)
    
    
    def set_shape(self, shape, dtype):
        """ Set the shape of the underlying data. This will allocate data
        and discard any pending subdata.
        """
        
        # Check
        dtype = np.dtype(dtype)
        if dtype.name not in self.DTYPE2GTYPE:
            raise ValueError('This data type is not allowed.')
        
        # If dtype is a structure with a unique field
        # we get this unique field as dtype
        if dtype.fields and len(dtype.fields) == 1:
            dtype = dtype[dtype.names[0]]
        
        
        if dtype.fields:
            # Structure dtype
            
            # Shape myst be int. Check nonzero
            size = int(shape)
            if size == 0:
                raise ValueError("Size error (cannot be 0).")
            
            # Set our params
            self._dtype    = dtype
            self._stride   = self._dtype.itemsize
            self._offset   = 0
            self._shape    = (size, 1)
            
            nbytes   = self._stride * size
            
            # Compute internal shape as (x,y) and base dtype
            dtype = self._dtype
            shape = [size,]
            if dtype.fields:
                if len(dtype.fields) == 1:
                    shape.extend( [np.prod(dtype[0].shape)] )
            else:
                self._dtype = dtype.base
                shape.extend( dtype.shape)
            self._shape = shape
        else:
            # Normal dtype
            
            # Store shape, dtype, offset, stride
            self._shape = tuple(shape)
            self._dtype = dtype
            self._offset = 0
            self._stride = dtype.itemsize
            
            nbytes = np.prod(self._shape) * dtype.itemsize
        
        # Correct shape
        if len(self._shape) == 1:
            self._shape = (self._shape[0],1)
        elif len(self._shape) > 2:
            self._shape = (np.prod(self._shape[:-1]), self._shape[:-1])
        self._shape = tuple(self._shape)
        
        
        if isinstance(self, NotARealBuffer):
            # Do not set data for real
            if not self._nonrealbuffer_initialized:
                self._nonrealbuffer_initialized = True
            else:
                raise RuntimeError('Cannot set shape on a %s.' % self.__class__.__name__)
        else:
            # Proceed with setting
            self.set_nbytes(self, nbytes)
    
    
    def set_data(self, data):
        """ Set the data. This discards any pending data.
        """
        
        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # If data is a structure array with a unique field
        # we get this unique field as data
        if data.dtype.fields and len(data.dtype.fields) == 1:
            data = data[data.dtype.names[0]]
        
        # Set dtype, stride and offset
        self._dtype = data.dtype
        self._stride = self._dtype.itemsize
        self._offset = 0

        # Compute internal shape as (x,y) and base dtype
        dtype = data.dtype
        shape = list(data.shape) or [1]
        
        if dtype.fields:
            # Structured array
            if len(dtype.fields) == 1:
                shape.append( np.prod(dtype[0].shape) )
        else:
            # Normal array
            self._dtype = dtype.base
            shape.extend(dtype.shape)
            
            # Check data type
            if self._dtype.name not in self.DTYPE2GTYPE:
                raise TypeError("Data type not allowed for this buffer: %s" % 
                                                self._dtype.name)
        
        # Correct shape
        if len(shape) == 1:
            shape = (shape[0], 1)
        elif len(shape) > 2:
            shape = (np.prod(shape[:-1]),shape[:-1])
        self._shape = shape

        # Data is a view on a structured array (no contiguous data) We know
        # that when setting data we'll have to make a local copy so we need
        # to compute the stride relative to GPU layout and not use the
        # stride of the original array.
        if data.base is not data:
            self._stride = self._dtype.itemsize * shape[-1]
        
        if isinstance(self, NotARealBuffer):
            # Do not set data for real
            if not self._nonrealbuffer_initialized:
                self._nonrealbuffer_initialized = True
            else:
                raise RuntimeError('Cannot set shape on a %s.' % self.__class__.__name__)
        else:
            # Proceed with setting
            Buffer.set_data(self, data)
    
    
    def set_subdata(self, offset, data):
        """ Set subdata. The 
        """
        
        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Check shape and dtype
        # Note that we raise if dtype does not match while __setitem__ auto-converts
        if data.shape[1:] != self._shape[1:]:
            raise ValueError('Given data does not match with the current shape.')
        if data.dtype != self._dtype:
            raise ValueError('Given data does not match with the current dtype.')
        
        # Turn attribute-offset into a byte offset
        offset = int(offset)
        byte_offset = offset * self._stride
        
        
        if isinstance(self, NotARealBuffer):
            # Do not set data for real
            if not self._nonrealbuffer_initialized:
                self._nonrealbuffer_initialized = True
            else:
                raise RuntimeError('Cannot set shape on a %s.' % self.__class__.__name__)
        else:
            # Proceed with setting
            Buffer.set_subdata(self, byte_offset, data)




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
    
    # Note that we do not actually use this, except the keys to test
    # whether a data type is allowed; we parse the gtype from the
    # attribute data.
    DTYPE2GTYPE = { 'int8': gl.GL_BYTE,
                    'uint8': gl.GL_UNSIGNED_BYTE,
                    'uint16': gl.GL_UNSIGNED_SHORT,
                    'int16': gl.GL_SHORT,
                    'float32': gl.GL_FLOAT,
                    'float16': gl.ext.GL_HALF_FLOAT,
                    }


    def __init__(self, data=None, dtype=None):
        DataBuffer.__init__(self, data, dtype, target=gl.GL_ARRAY_BUFFER)


class NotARealBuffer:
    pass


# ------------------------------------------------------ VertexBuffer class ---
class VertexBufferView(VertexBuffer, NotARealBuffer):
    """ A VertexBufferView is a view on another buffer

    See VerteBuffer for usage.
    """

    def __init__(self, data=None, dtype=None, base=None, offset=0):
        """ Initialize the view """
        VertexBuffer.__init__(self, data, dtype)
        
        self._base = base
        self._offset = offset
        self._stride = base.stride  # Override this
        
        # Check dtype
        if self._dtype.name not in self.DTYPE2GTYPE:
            raise TypeError("Data type not allowed for this buffer: %s" % 
                                                self._dtype.name)
    
    
    @property
    def handle(self):
        # Handle on base buffer. 
        self._handle = self._base._handle
        return self._handle
    
    
    @property
    def stride(self):
        """ Byte number separating two elements. """
        self._stride = self._base.stride
        return self._stride
    
    
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
    
    # We need a DTYPE->GL map for the element buffer. Used in program.draw()
    DTYPE2GTYPE = { 'uint8': gl.GL_UNSIGNED_BYTE,
                    'uint16': gl.GL_UNSIGNED_SHORT,
                    'uint32': gl.GL_UNSIGNED_INT,
                    }
    
    def __init__(self, data=None, dtype=None, size=0):
        DataBuffer.__init__(self, data, dtype, target=gl.GL_ELEMENT_ARRAY_BUFFER)
        
        # todo: AK: me no get this, pyopengl will make the data contigious if needed
#         if self._shape[1] != 1:
#             raise TypeError("Only contiguous data allowed for this buffer")




# ------------------------------------------------ ClientVertexBuffer class ---
class ClientVertexBuffer(VertexBuffer, NotARealBuffer):
    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer. It merely serves as
    passing direct data during a drawing operations.
    
    Note this kind of buffer is highly inefficient since data is uploaded at
    each drawing operations.
    """

    def __init__(self, data):
        """ Initialize the buffer. """
        VertexBuffer.__init__(self, data)
        self._data = data
    
    @property
    def data(self):
        """ Buffer data. """
        return self._data
    
    
    def __getitem__(self, key):        pass
    def __setitem__(self, key, data):  pass
    def _create(self):                 pass
    def _delete(self):                 pass
    def _activate(self):               pass
    def _deactivate(self):             pass
    def _update(self):                 pass


class ClientElementBuffer(ElementBuffer, NotARealBuffer):
    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer. It merely serves as
    passing direct data during a drawing operations.
    
    Note this kind of buffer is highly inefficient since data is uploaded at
    each drawing operations.
    """

    def __init__(self, data):
        """ Initialize the buffer. """
        ElementBuffer.__init__(self, data)
        self._data = data
    
    @property
    def data(self):
        """ Buffer data. """
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
        print("Shape",     P.shape)
        print("Offset:",  P.offset)
        print("Stride:",  P.stride)
        print()

    V[10:20] = data[10:20]
    V[...] = data
    print( len(V._pending_data))
    #V[10:20] = data[10:19]
    #V[10:20] = data[10:21]

    I = ElementBuffer(indices)
    print("Shape",     I.shape)
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
