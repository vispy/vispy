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
        with self.assertRaises(ValueError):
            buffer.set_data(data)

        buffer = Buffer(data=data,target=gl.GL_ARRAY_BUFFER)
        assert len(buffer._pending_data) == 1

        buffer.set_data(data)
        assert len(buffer._pending_data) == 1

        buffer.set_data(data[:50], offset=0)
        assert len(buffer._pending_data) == 2

        buffer.set_data(data)
        assert len(buffer._pending_data) == 1


# -----------------------------------------------------------------------------
class DataBufferTest(unittest.TestCase):

    def test_init(self):
        data = np.zeros(100, np.float32)
        buffer = DataBuffer(data=data, target=gl.GL_ARRAY_BUFFER)
        assert buffer._size   == 100
        assert buffer._dtype  == np.float32

    def test_types(self):
        data = np.zeros(100, np.float32)
        buffer = DataBuffer(data=data, target=gl.GL_ARRAY_BUFFER)
        # assert buffer.gtype == gl.GL_FLOAT
        assert buffer.size == 100

        data = np.zeros(100, [('a', np.float32, 1)])
        buffer = DataBuffer(data=data, target=gl.GL_ARRAY_BUFFER)
        # assert buffer.gtype == gl.GL_FLOAT
        assert buffer.size == 100

        data = np.zeros(100, [('a', np.float32, 4)])
        buffer = DataBuffer(data=data, target=gl.GL_ARRAY_BUFFER)
        # assert buffer.gtype == gl.GL_FLOAT_VEC4
        assert buffer.size == 100

        data = np.zeros(100, [('a', np.float32, (4,4))])
        buffer = DataBuffer(data=data, target=gl.GL_ARRAY_BUFFER)
        # assert buffer.gtype == gl.GL_FLOAT_MAT4
        assert buffer.size == 100


# -----------------------------------------------------------------------------
class VertexBufferTest(unittest.TestCase):

    def test_init(self):
        data = np.zeros(100, np.float32)
        buffer = VertexBuffer(data=data)
        assert buffer.size   == 100
        assert buffer.dtype  == np.float32

    def test_resize(self):

        # Resize allowed with set_data (and offset=0)
        V = VertexBuffer(size=100, dtype=np.float32)
        V.set_data(np.ones(200, np.float32))
        assert V.size == 200

        # Resize not allowed with set_subdata
        with self.assertRaises(ValueError):
            V.set_subdata(np.ones(300, np.float32))



    def test_offset(self):
        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        assert buffer['position'].offset == 0
        assert buffer['texcoord'].offset == 3*np.dtype(np.float32).itemsize
        assert buffer['color'].offset    == (3+2)*np.dtype(np.float32).itemsize


    def test_setitem(self):
        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        with self.assertRaises(ValueError):
            buffer['color'] = data['color']

        buffer[...] = data
        assert len(buffer._pending_data) == 1

        buffer[10:20] = data[10:20]
        assert len(buffer._pending_data) == 2


    def test_set_data(self):

        dtype = np.dtype( [ ('position', np.float32, 3),
                            ('texcoord', np.float32, 2),
                            ('color',    np.float32, 4) ] )
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        buffer[10:20] = data[10:20]
        assert len(buffer._pending_data) == 2
        buffer[...] = data
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
        assert buffer._size  == 100
        assert buffer._dtype == np.uint32


    def test_typechecking(self):

        data = np.zeros(100, [('index', np.uint32,1)])
        buffer = ElementBuffer(data=data)
        assert len(buffer._pending_data) == 1

        data = np.zeros(100, [('index', np.uint32,2)])
        with self.assertRaises(TypeError):
            buffer = ElementBuffer(data=data)

        data = np.zeros(100, [('a', np.uint32, 1),
                              ('b', np.uint32, 1) ])
        with self.assertRaises(TypeError):
            buffer = ElementBuffer(data=data)

        data = np.zeros(100, np.float32)
        with self.assertRaises(TypeError):
            buffer = ElementBuffer(data=data)
        


if __name__ == "__main__":
    unittest.main()
