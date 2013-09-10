# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from vispy import gl

from vispy.oogl.buffer import Buffer
from vispy.oogl.buffer import DataBuffer
from vispy.oogl.buffer import VertexBuffer
from vispy.oogl.buffer import ElementBuffer



# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    def test_init(self):
        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)
        assert buffer._handle      == 0
        assert buffer._need_update == False
        assert buffer._valid       == False
        assert buffer._nbytes      == 0
        assert buffer._usage       == gl.GL_DYNAMIC_DRAW

    def test_pending_data(self):
        data = np.zeros(100, np.float32)

        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)
        assert len(buffer._pending_data) == 0
        
        buffer = Buffer(data=data, target=gl.GL_ARRAY_BUFFER)
        assert len(buffer._pending_data) == 1

        buffer.set_data(data)
        assert len(buffer._pending_data) == 1

        buffer.set_subdata(0, data[:50])
        assert len(buffer._pending_data) == 2

        buffer.set_data(data)
        assert len(buffer._pending_data) == 1



# -----------------------------------------------------------------------------
class VertexBufferTest(unittest.TestCase):

    def test_init(self):
        data = np.zeros(100, np.float32)
        buffer = VertexBuffer(data=data)
        assert buffer.count == 100
        assert buffer.vsize == 1
        assert buffer.dtype == np.float32
    
    
    def test_init_with_data(self):
        
        data = np.zeros(100, np.float32)
        buffer = VertexBuffer(data)
        assert buffer.count == 100
        assert buffer.vsize == 1
        
        data = np.zeros((100, 1), np.float32)
        buffer = VertexBuffer(data)
        assert buffer.count == 100
        assert buffer.vsize == 1

        data = np.zeros((100,4), np.float32)
        buffer = VertexBuffer(data)
        assert buffer.count == 100
        assert buffer.vsize == 4
    
    
    def test_init_with_structured_data(self):
        
        # Singular 1
        data = np.zeros(100, [('a', np.float32, 1)])
        buffer = VertexBuffer(data)
        assert buffer.count == 100
        assert buffer.vsize == 1
        assert buffer.dtype == np.float32
        
        # Singular 2
        data = np.zeros(100, [('a', np.float32, 4)])
        buffer = VertexBuffer(data)
        assert buffer.count == 100
        assert buffer.vsize == 4
        assert buffer.dtype == np.float32
        
        
        # Multple
        data = np.zeros(100, [ ('a', np.float32, 1),
                               ('b', np.uint8, 2),
                               ('c', np.int16, 3) ] )
        buffer = VertexBuffer(data)
        
        assert buffer.vsize == 1
        assert buffer.dtype == data.dtype
        
        assert buffer['a'].vsize == 1
        assert buffer['a'].dtype == np.float32

        assert buffer['b'].vsize == 2
        assert buffer['b'].dtype == np.uint8

        assert buffer['c'].vsize == 3
        assert buffer['c'].dtype == np.int16
    
    
    def test_init_with_dtype(self):
        
        # Single element, this is simply unraveled
        dtype = np.dtype([('a',np.float32,4)])
        buffer = VertexBuffer(dtype)
        assert buffer.count == 0
        assert buffer.vsize == 4
        assert buffer.dtype == np.float32
        
        # Short notation specific to VertexBuffer
        buffer = VertexBuffer(('a',np.float32,4))
        assert buffer.vsize == 4
        assert buffer.dtype == np.float32
        
        # Plain dtype descriptor
        buffer = VertexBuffer(np.float32)
        assert buffer.vsize == 1
        assert buffer.dtype == np.float32
        
        # String dtype descirptor
        buffer = VertexBuffer('float32')
        assert buffer.vsize == 1
        assert buffer.dtype == np.float32
        
        # Multiple elements
        dtype = dtype=[('a',np.float32,4), ('b',np.uint8,2)]
        buffer = VertexBuffer(dtype)
        assert buffer.count == 0
        assert buffer.vsize == 1
        assert buffer.dtype == np.dtype(dtype)
        #
        subbuffer = buffer['a']
        assert subbuffer.count == 0
        assert subbuffer.vsize == 4
        assert subbuffer.dtype == np.float32
        #
        subbuffer = buffer['b']
        assert subbuffer.count == 0
        assert subbuffer.vsize == 2
        assert subbuffer.dtype == np.uint8
    
    
    def test_resize(self):
        
        # Resize allowed with set_data (and offset=0)
        V = VertexBuffer(np.float32)
        V.set_data(np.ones(200, np.float32))
        assert V.count == 200
        
        V.set_data(np.ones(300, np.float32))
        assert V.count == 300
        
        # Resize not allowed with set_subdata
        with self.assertRaises(ValueError):
            V.set_subdata(0, np.ones(400, np.float32))
    

    def test_offset(self):
        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)
        
        assert buffer['position'].offset == 0
        assert buffer['texcoord'].offset == 3*np.dtype(np.float32).itemsize
        assert buffer['color'].offset    == (3+2)*np.dtype(np.float32).itemsize
    
    
    


    def test_stride(self):
        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        assert buffer['position'].stride == 9*np.dtype(np.float32).itemsize
        assert buffer['texcoord'].stride == 9*np.dtype(np.float32).itemsize
        assert buffer['color'].stride    == 9*np.dtype(np.float32).itemsize


        buffer = VertexBuffer(data['position'])
        assert buffer.offset == 0
        assert buffer.stride == 3*np.dtype(np.float32).itemsize



    def test_setitem(self):
        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        with self.assertRaises(ValueError):
            buffer['color'] = data['color']
        
        buffer[...] = data
        assert len(buffer._pending_data) == 2

        buffer[10:20] = data[10:20]
        assert len(buffer._pending_data) == 3
    
        # Discart all pending data
        buffer.set_data(data)
        assert len(buffer._pending_data) == 1
        
        with self.assertRaises(ValueError):
            buffer[10:20] = data[10:19]

        with self.assertRaises(ValueError):
            buffer[10:20] = data[10:21]



# -----------------------------------------------------------------------------
class ElementBufferTest(unittest.TestCase):

    def test_init(self):
        data = np.zeros(100, np.uint32)
        buffer = ElementBuffer(data=data)
        assert buffer.count == 100
        assert buffer.dtype == np.uint32

    
    def test_shape_agnostic(self):
        
        data = np.zeros(100, np.uint32)
        buffer = ElementBuffer(data=data)
        assert buffer.count == data.size
        assert buffer.vsize == 1
        
        data.shape = 50, 2
        buffer = ElementBuffer(data=data)
        assert buffer.count == data.size
        assert buffer.vsize == 1
        
        data.shape = 10, 5, 2
        buffer = ElementBuffer(data=data)
        assert buffer.count == data.size
        assert buffer.vsize == 1
    
    
    def test_typechecking(self):
        
        # Elementbuffer does support for structured arrays
        data = np.zeros(100, [('index', np.uint32,1)])
        with self.assertRaises(ValueError):
            buffer = ElementBuffer(data=data)


if __name__ == "__main__":
    unittest.main()
