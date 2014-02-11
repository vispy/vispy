# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from vispy.gloo import gl

from vispy.gloo.buffer import (VertexBuffer, ClientVertexBuffer,
                               ElementBuffer, ClientElementBuffer,
                               Buffer, DataBuffer)


# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    def test_init(self):
        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)
        assert buffer._handle == 0
        assert buffer._need_update is False
        assert buffer._valid is False
        assert buffer._nbytes == 0
        assert buffer._usage == gl.GL_DYNAMIC_DRAW

    def test_pending_data(self):
        data = np.zeros(100, np.float32)

        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)
        self.assertEqual(len(buffer._pending_data), 0)

        buffer = Buffer(data=data, target=gl.GL_ARRAY_BUFFER)
        self.assertEqual(len(buffer._pending_data), 1)

        buffer.set_data(data)
        self.assertEqual(len(buffer._pending_data), 1)

        buffer.set_subdata(0, data[:50])
        self.assertEqual(len(buffer._pending_data), 2)

        buffer.set_data(data)
        self.assertEqual(len(buffer._pending_data), 1)

    def test_setting_size(self):
        data = np.zeros(100, np.float32)
        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)

        buffer.set_data(data)
        self.assertEqual(buffer.nbytes, data.nbytes)

        buffer.set_data(np.zeros(200, np.float32))
        self.assertEqual(buffer.nbytes, 200 * 4)

        buffer.set_nbytes(10)
        self.assertEqual(buffer.nbytes, 10)

        buffer.set_nbytes(20)
        self.assertEqual(buffer.nbytes, 20)

    def test_setting_subdata(self):

        data = np.zeros(100, np.float32)
        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)

        # Set subdata when no data is set
        self.assertRaises(RuntimeError, buffer.set_subdata, 0, data)

        # Set nbytes and try again
        buffer.set_nbytes(data.nbytes)
        buffer.set_subdata(0, data)

        # Subpart
        buffer.set_subdata(0, data[:50])
        buffer.set_subdata(50, data[50:])

        # Too big
        self.assertRaises(ValueError, buffer.set_subdata, 1, data)

        # Weird
        self.assertRaises(ValueError, buffer.set_subdata, -1, data)

        # Weirder
        self.assertRaises(ValueError, buffer.set_subdata, 1000000, data)

    def test_wrong_data(self):
        buffer = Buffer(target=gl.GL_ARRAY_BUFFER)

        # String
        self.assertRaises(ValueError, buffer.set_data, 'foo')

        # Bytes
        some_bytes = 'foo'.encode('utf-8')
        self.assertRaises(ValueError, buffer.set_data, some_bytes)

        # Now with subdata
        data = np.zeros(100, np.float32)
        buffer.set_data(data)

        # String
        self.assertRaises(ValueError, buffer.set_subdata, 0, 'foo')
        self.assertRaises(ValueError, buffer.set_subdata, 'foo', data)

        # Bytes
        some_bytes = 'foo'.encode('utf-8')
        self.assertRaises(ValueError, buffer.set_subdata, 0, some_bytes)
        self.assertRaises(ValueError, buffer.set_subdata, some_bytes, data)


# -----------------------------------------------------------------------------
class DataBufferTest(unittest.TestCase):
    def test_buffer(self):
        self.assertRaises(NotImplementedError, DataBuffer, gl.GL_ARRAY_BUFFER,
                          'float32')
        self.assertRaises(ValueError, DataBuffer, gl.GL_ARRAY_BUFFER, 1.5)


# -----------------------------------------------------------------------------
class VertexBufferTest(unittest.TestCase):

    def test_init(self):
        data = np.zeros(100, np.float32)
        buffer = VertexBuffer(data=data)
        assert buffer.count == 100
        assert buffer.vsize == 1
        assert buffer.dtype == np.float32

    def test_init_with_data(self):

        for dtype in (np.float32, np.uint8, np.int16):

            data = np.zeros(100, dtype)
            buffer = VertexBuffer(data)
            assert buffer.count == 100
            assert buffer.vsize == 1
            assert buffer.dtype == dtype

            data = np.zeros((100, 1), dtype)
            buffer = VertexBuffer(data)
            assert buffer.count == 100
            assert buffer.vsize == 1
            assert buffer.dtype == dtype

            data = np.zeros((100, 4), dtype)
            buffer = VertexBuffer(data)
            assert buffer.count == 100
            assert buffer.vsize == 4
            assert buffer.dtype == dtype

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
        data = np.zeros(100, [('a', np.float32, 1),
                              ('b', np.uint8, 2),
                              ('c', np.int16, 3)])
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
        dtype = np.dtype([('a', np.float32, 4)])
        buffer = VertexBuffer(dtype)
        assert buffer.count == 0
        assert buffer.vsize == 4
        assert buffer.dtype == np.float32

        # Short notation specific to VertexBuffer
        buffer = VertexBuffer(('a', np.float32, 4))
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
        dtype = dtype = [('a', np.float32, 4), ('b', np.uint8, 2)]
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
        self.assertRaises(ValueError, V.set_subdata, 0,
                          np.ones(400, np.float32))

    def test_offset(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color', np.float32, 4)])
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        assert buffer['position'].offset == 0
        assert buffer['texcoord'].offset == 3 * np.dtype(np.float32).itemsize
        assert buffer['color'].offset == (
            3 + 2) * np.dtype(np.float32).itemsize

    def test_stride(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color', np.float32, 4)])
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        assert buffer['position'].stride == 9 * np.dtype(np.float32).itemsize
        assert buffer['texcoord'].stride == 9 * np.dtype(np.float32).itemsize
        assert buffer['color'].stride == 9 * np.dtype(np.float32).itemsize

        buffer = VertexBuffer(data['position'])
        assert buffer.offset == 0
        assert buffer.stride == 3 * np.dtype(np.float32).itemsize

    def test_setitem(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color', np.float32, 4)])
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)

        def setter(b, d):
            b['color'] = d['color']
        self.assertRaises(ValueError, setter, buffer, data)

        buffer[...] = data
        self.assertEqual(len(buffer._pending_data), 2)

        buffer[10:20] = data[10:20]
        self.assertEqual(len(buffer._pending_data), 3)

        # Discart all pending data
        buffer.set_data(data)
        self.assertEqual(len(buffer._pending_data), 1)

        def setter(b, d):
            b[10:20] = d[10:19]
        self.assertRaises(ValueError, setter, buffer, data)

        def setter(b, d):
            buffer[10:20] = data[10:21]
        self.assertRaises(ValueError, setter, buffer, data)

    def test_set_data_on_view(self):

        dtype = np.dtype([('a', np.float32, 3),
                          ('b', np.float32, 2),
                          ('c', np.float32, 4)])
        data = np.zeros(100, dtype=dtype)
        buffer = VertexBuffer(data)
        self.assertRaises(RuntimeError, buffer['a'].set_count, 100)
        self.assertRaises(RuntimeError, buffer['a'].set_data, data['a'])
        self.assertRaises(RuntimeError, buffer['a'].set_subdata, data['a'])

    def test_client_buffer(self):
        data = np.zeros((100, 3), dtype=np.float32)
        buffer = ClientVertexBuffer(data)
        self.assertTrue(buffer.data is data)
        # these are all "pass"
        buffer['hi'] = 1
        self.assertTrue(buffer['hi'] is None)
        self.assertTrue(buffer._create() is None)
        self.assertTrue(buffer._delete() is None)
        self.assertTrue(buffer._activate() is None)
        self.assertTrue(buffer._deactivate() is None)
        self.assertTrue(buffer._update() is None)

        self.assertRaises(RuntimeError, buffer.set_data, data)
        self.assertRaises(RuntimeError, buffer.set_subdata, data)

    def test_typechecking(self):

        # VertexBuffer supports these
        for dtype in (np.uint8, np.int8, np.uint16, np.int16,
                      np.float32, np.float16):
            VertexBuffer(dtype)

        # VertexBuffer does *not* support these
        float128 = getattr(np, 'float128', np.float64)  # may not exist
        for dtype in (np.uint32, np.int32, np.float64, float128):
            self.assertRaises(TypeError, VertexBuffer, dtype)


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
        data = np.zeros(100, [('index', np.uint32, 1)])
        self.assertRaises(ValueError, ElementBuffer, data=data)

        # ElementBuffer supports these
        for dtype in (np.uint8, np.uint16, np.uint32):
            ElementBuffer(dtype)

        # ElementBuffer does *not* support these
        for dtype in (np.int8, np.int16, np.int32, np.float32, np.float64):
            self.assertRaises(TypeError, ElementBuffer, dtype)

    def test_client_buffer(self):
        data = np.zeros((100, 3), dtype=np.uint32)
        self.assertRaises(ValueError, ClientElementBuffer, 'me')
        b = ClientElementBuffer(data)
        self.assertTrue(b.data is data)

        for fun in (b.set_data, b.set_subdata, b.set_count):
            self.assertRaises(RuntimeError, fun)
        # these all "pass"
        b['me'] = 1
        self.assertTrue(b['me'] is None)
        self.assertTrue(b._create() is None)
        self.assertTrue(b._delete() is None)
        self.assertTrue(b._activate() is None)
        self.assertTrue(b._deactivate() is None)
        self.assertTrue(b._update() is None)
