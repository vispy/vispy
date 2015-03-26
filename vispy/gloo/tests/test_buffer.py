# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.testing import run_tests_if_main
from vispy.gloo.buffer import (Buffer, DataBuffer, DataBufferView, 
                               VertexBuffer, IndexBuffer)


# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    # Default init
    # ------------
    def test_init_default(self):
        """ Test buffer init"""
        
        # No data
        B = Buffer()
        assert B.nbytes == 0
        glir_cmd = B._glir.clear()[-1]
        assert glir_cmd[0] == 'CREATE'
        
        # With data
        data = np.zeros(100)
        B = Buffer(data=data)
        assert B.nbytes == data.nbytes
        glir_cmd = B._glir.clear()[-1]
        assert glir_cmd[0] == 'DATA'
        
        # With nbytes
        B = Buffer(nbytes=100)
        assert B.nbytes == 100
        glir_cmd = B._glir.clear()[-1]
        assert glir_cmd[0] == 'SIZE'
        
        # Wrong data
        self.assertRaises(ValueError, Buffer, data, 4)
        self.assertRaises(ValueError, Buffer, data, data.nbytes)

    # Check setting the whole buffer clear pending operations
    # -------------------------------------------------------
    def test_set_whole_data(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        B._glir.clear()
        B.set_data(data=data)
        glir_cmds = B._glir.clear()
        assert len(glir_cmds) == 2
        assert glir_cmds[0][0] == 'SIZE'
        assert glir_cmds[1][0] == 'DATA'
    
        # And sub data
        B.set_subdata(data[:50], 20)
        glir_cmds = B._glir.clear()
        assert len(glir_cmds) == 1
        assert glir_cmds[0][0] == 'DATA'
        assert glir_cmds[0][2] == 20  # offset
        
        # And sub data
        B.set_subdata(data)
        glir_cmds = B._glir.clear()
        assert glir_cmds[-1][0] == 'DATA'
        
        # Wrong ways to set subdata
        self.assertRaises(ValueError, B.set_subdata, data[:50], -1)  # neg
        self.assertRaises(ValueError, B.set_subdata, data, 10)  # no fit
        
    # Check stored data is data
    # -------------------------
    def test_data_storage(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        B.set_data(data=data[:50], copy=False)
        glir_cmd = B._glir.clear()[-1]
        assert glir_cmd[-1].base is data

    # Check setting oversized data
    # ----------------------------
    def test_oversized_data(self):
        data = np.zeros(10)
        B = Buffer(data=data)
        # with self.assertRaises(ValueError):
        #    B.set_data(np.ones(20))
        self.assertRaises(ValueError, B.set_subdata, np.ones(20), offset=0)

    # Check negative offset
    # ---------------------
    def test_negative_offset(self):
        data = np.zeros(10)
        B = Buffer(data=data)
        # with self.assertRaises(ValueError):
        #    B.set_data(np.ones(1), offset=-1)
        self.assertRaises(ValueError, B.set_subdata, np.ones(1), offset=-1)

    # Check offlimit offset
    # ---------------------
    def test_offlimit_offset(self):
        data = np.zeros(10)
        B = Buffer(data=data)
        # with self.assertRaises(ValueError):
        #    B.set_data(np.ones(1), offset=10 * data.dtype.itemsize)
        self.assertRaises(ValueError, B.set_subdata,
                          np.ones(1), offset=10 * data.dtype.itemsize)

    # Buffer size
    # -----------
    def test_buffer_size(self):
        data = np.zeros(10)
        B = Buffer(data=data)
        assert B.nbytes == data.nbytes

    # Resize
    # ------
    def test_buffer_resize(self):
        data = np.zeros(10)
        B = Buffer(data=data)
        data = np.zeros(20)
        B.set_data(data)
        assert B.nbytes == data.nbytes


# -----------------------------------------------------------------------------
class DataBufferTest(unittest.TestCase):

    # Default init
    # ------------
    def test_default_init(self):
        # Check default storage and copy flags
        data = np.ones(100)
        B = DataBuffer(data)
        assert B.nbytes == data.nbytes
        assert B.offset == 0
        assert B.size == 100
        assert B.itemsize == data.itemsize
        assert B.stride == data.itemsize
        assert B.dtype == data.dtype
        
        # Given data must be actual numeric data
        self.assertRaises(TypeError, DataBuffer, 'this is not nice data')
    
    # Default init with structured data
    # ---------------------------------
    def test_structured_init(self):
        # Check structured type
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        assert B.nbytes == data.nbytes
        assert B.offset == 0
        assert B.size == 10
        assert B.itemsize == data.itemsize
        assert B.stride == data.itemsize
        assert B.dtype == data.dtype
        
    # No CPU storage
    # --------------
    def test_no_storage_copy(self):
        data = np.ones(100, np.float32)
        B = DataBuffer(data)
        assert B.stride == 4

    # Wrong storage
    # -------------
    def test_non_contiguous_storage(self):
        # Ask to have CPU storage and to use data as storage
        # Not possible since data[::2] is not contiguous
        data = np.ones(100, np.float32)
        data_given = data[::2]
        
        B = DataBuffer(data_given)
        assert B.stride == 4*2
    
    # Get buffer field
    # ----------------
    def test_getitem_field(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)

        Z = B["position"]
        assert Z.nbytes == 10 * 3 * np.dtype(np.float32).itemsize
        assert Z.offset == 0
        assert Z.size == 10
        assert Z.itemsize == 3 * np.dtype(np.float32).itemsize
        assert Z.stride == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.dtype == (np.float32, 3)

        Z = B["texcoord"]
        assert Z.nbytes == 10 * 2 * np.dtype(np.float32).itemsize
        assert Z.offset == 3 * np.dtype(np.float32).itemsize
        assert Z.size == 10
        assert Z.itemsize == 2 * np.dtype(np.float32).itemsize
        assert Z.stride == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.dtype == (np.float32, 2)

        Z = B["color"]
        assert Z.nbytes == 10 * 4 * np.dtype(np.float32).itemsize
        assert Z.offset == (2 + 3) * np.dtype(np.float32).itemsize
        assert Z.size == 10
        assert Z.itemsize == 4 * np.dtype(np.float32).itemsize
        assert Z.stride == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.dtype == (np.float32, 4)

    # Get view via index
    # ------------------
    def test_getitem_index(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        Z = B[0:1]
        assert Z.base == B
        assert Z.id == B.id
        assert Z.nbytes == 1 * (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.offset == 0
        assert Z.size == 1
        assert Z.itemsize == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.stride == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.dtype == B.dtype
        assert 'DataBufferView' in repr(Z)
        
        # There's a few things we cannot do with a view
        self.assertRaises(RuntimeError, Z.set_data, data)
        self.assertRaises(RuntimeError, Z.set_subdata, data)
        self.assertRaises(RuntimeError, Z.resize_bytes, 20)
        self.assertRaises(RuntimeError, Z.__getitem__, 3)
        self.assertRaises(RuntimeError, Z.__setitem__, 3, data)
    
    # View get invalidated when base is resized
    # -----------------------------------------
    def test_invalid_view_after_resize(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        Y = B['position']
        Z = B[5:]
        B.resize_bytes(5)
        assert Y._valid is False
        assert Z._valid is False

    # View get invalidated after setting oversized data
    # -------------------------------------------------
    def test_invalid_view_after_set_data(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        Z = B[5:]
        B.set_data(np.zeros(15, dtype=dtype))
        assert Z._valid is False

    # Set data on base buffer : ok
    # ----------------------------
    def test_set_data_base(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        B.set_data(data)
        last_cmd = B._glir.clear()[-1]
        assert last_cmd[0] == 'DATA'
        
        # Extra kwargs are caught
        self.assertRaises(TypeError, B.set_data, data, foo=4)
    
    # Check set_data using offset in data buffer
    # ------------------------------------------
    def test_set_data_offset(self):
        data = np.zeros(100, np.float32)
        subdata = data[:10]
        
        B = DataBuffer(data)
        B.set_subdata(subdata, offset=10)
        last_cmd = B._glir.clear()[-1]
        offset = last_cmd[2]
        assert offset == 10*4
    
    def test_getitem(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        assert B[1].dtype == dtype
        assert B[1].size == 1
        assert B[-1].dtype == dtype
        assert B[-1].size == 1
        
        self.assertRaises(IndexError, B.__getitem__, +999)
        self.assertRaises(IndexError, B.__getitem__, -999)
    
    def test_setitem(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        B[1] = data[0]
        B[-1] = data[0]
        B[:5] = data[:5]
        B[5:0] = data[:5]  # Weird, but we apparently support this
        B[1] = b''  # Gets conveted into array of dtype. Lists do not work
        
        self.assertRaises(IndexError, B.__setitem__, +999, data[0])
        self.assertRaises(IndexError, B.__setitem__, -999, data[0])
        self.assertRaises(TypeError, B.__setitem__, [], data[0])
        
    # Setitem + broadcast
    # ------------------------------------------------------
    def test_setitem_broadcast(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        self.assertRaises(ValueError, B.__setitem__, 'position', (1, 2, 3))

    # Set every 2 item
    # ------------------------------------------------------
    def test_setitem_strided(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data1 = np.zeros(10, dtype=dtype)
        data2 = np.ones(10, dtype=dtype)
        B = DataBuffer(data1)
        s = slice(None, None, 2)
        self.assertRaises(ValueError, B.__setitem__, s, data2[::2])

    # Set half the array
    # ------------------------------------------------------
    def test_setitem_half(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data1 = np.zeros(10, dtype=dtype)
        data2 = np.ones(10, dtype=dtype)
        B = DataBuffer(data1)
        B._glir.clear()
        B[:5] = data2[:5]
        glir_cmds = B._glir.clear()
        assert len(glir_cmds) == 1
        set_data = glir_cmds[0][-1]
        assert np.allclose(set_data['position'], data2['position'][:5])
        assert np.allclose(set_data['texcoord'][:5], data2['texcoord'][:5])
        assert np.allclose(set_data['color'][:5], data2['color'][:5])

    # Set field without storage: error
    # --------------------------------
    def test_setitem_field_no_storage(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        self.assertRaises(ValueError,  B.__setitem__, 'position', (1, 2, 3))

    # Set every 2 item without storage:  error
    # ----------------------------------------
    def test_every_two_item_no_storage(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        # with self.assertRaises(ValueError):
        #    B[::2] = data[::2]
        s = slice(None, None, 2)
        self.assertRaises(ValueError, B.__setitem__, s, data[::2])

    # Resize
    # ------
    def test_resize(self):
        data = np.zeros(10)
        B = DataBuffer(data=data)
        data = np.zeros(20)
        B.set_data(data)
        assert B.nbytes == data.nbytes

    # Resize now allowed using ellipsis
    # -----------------------------
    def test_no_resize_ellipsis(self):
        data = np.zeros(10)
        B = DataBuffer(data=data)
        data = np.zeros(30)
        self.assertRaises(ValueError, B.__setitem__, Ellipsis, data)
        
    # Broadcast when using ellipses
    def test_broadcast_ellipsis(self):
        data = np.zeros(10)
        B = DataBuffer(data=data)
        data = np.zeros(5)
        B[Ellipsis] = data
        glir_cmd = B._glir.clear()[-1]
        assert glir_cmd[-1].shape == (10,)


class DataBufferViewTest(unittest.TestCase):
    
    def test_init_view(self):
        data = np.zeros(10)
        B = DataBuffer(data=data)
        
        V = DataBufferView(B, 1)
        assert V.size == 1
        
        V = DataBufferView(B, slice(0, 5))
        assert V.size == 5
        
        V = DataBufferView(B, slice(5, 0))
        assert V.size == 5
        
        V = DataBufferView(B, Ellipsis)
        assert V.size == 10
        
        self.assertRaises(TypeError, DataBufferView, B, [])
        self.assertRaises(ValueError, DataBufferView, B, slice(0, 10, 2))
        
        
# -----------------------------------------------------------------------------
class VertexBufferTest(unittest.TestCase):

    # VertexBuffer allowed base types
    # -------------------------------
    def test_init_allowed_dtype(self):
        for dtype in (np.uint8, np.int8, np.uint16, np.int16, np.float32):
            V = VertexBuffer(np.zeros((10, 3), dtype=dtype))
            names = V.dtype.names
            assert V.dtype[names[0]].base == dtype
            assert V.dtype[names[0]].shape == (3,)
        for dtype in (np.float64, np.int64):
            self.assertRaises(TypeError, VertexBuffer,
                              np.zeros((10, 3), dtype=dtype))

        # Tuple/list is also allowed
        V = VertexBuffer([1, 2, 3])
        assert V.size == 3
        assert V.itemsize == 4
        #
        V = VertexBuffer([[1, 2], [3, 4], [5, 6]])
        assert V.size == 3
        assert V.itemsize == 2 * 4
        
        # Convert
        data = np.zeros((10,), 'uint8')
        B = VertexBuffer(data)
        assert B.dtype[0].base == np.uint8
        assert B.dtype[0].itemsize == 1
        #
        data = np.zeros((10, 2), 'uint8')
        B = VertexBuffer(data)
        assert B.dtype[0].base == np.uint8
        assert B.dtype[0].itemsize == 2
        B.set_data(data, convert=True)
        assert B.dtype[0].base == np.float32
        assert B.dtype[0].itemsize == 8
        B = VertexBuffer(data[::2].copy())
        
        # This is converted to 1D
        B = VertexBuffer([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]])
        assert B.size == 10 
         
        # Not allowed
        self.assertRaises(TypeError, VertexBuffer, dtype=np.float64)
        #self.assertRaises(TypeError, VertexBuffer, [[1,2,3,4,5],[1,2,3,4,5]])

    # VertexBuffer not allowed base types
    # -----------------------------------
    def test_init_not_allowed_dtype(self):
        for dtype in (np.uint32, np.int32, np.float64):
            # with self.assertRaises(TypeError):
            #    V = VertexBuffer(dtype=dtype)
            self.assertRaises(TypeError, VertexBuffer, dtype=dtype)

    def test_glsl_type(self):
        
        data = np.zeros((10,), np.float32)
        B = VertexBuffer(data)
        C = B[1:]
        assert B.glsl_type == ('attribute', 'float')
        assert C.glsl_type == ('attribute', 'float')
        
        data = np.zeros((10, 2), np.float32)
        B = VertexBuffer(data)
        C = B[1:]
        assert B.glsl_type == ('attribute', 'vec2')
        assert C.glsl_type == ('attribute', 'vec2')
        
        data = np.zeros((10, 4), np.float32)
        B = VertexBuffer(data)
        C = B[1:]
        assert B.glsl_type == ('attribute', 'vec4')
        assert C.glsl_type == ('attribute', 'vec4')


# -----------------------------------------------------------------------------
class IndexBufferTest(unittest.TestCase):

    # IndexBuffer allowed base types
    # ------------------------------
    def test_init_allowed_dtype(self):
        
        # allowed dtypes
        for dtype in (np.uint8, np.uint16, np.uint32):
            b = IndexBuffer(np.zeros(10, dtype=dtype))
            b.dtype == dtype

        # no data => no dtype
        V = IndexBuffer()
        V.dtype is None
        
        # Not allowed dtypes
        for dtype in (np.int8, np.int16, np.int32,
                      np.float16, np.float32, np.float64):
            # with self.assertRaises(TypeError):
            #    V = IndexBuffer(dtype=dtype)
            data = np.zeros(10, dtype=dtype)
            self.assertRaises(TypeError, IndexBuffer, data)
        
        # Prepare some data
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2), ])
        sdata = np.zeros(10, dtype=dtype)
        
        # Normal data is
        data = np.zeros([1, 2, 3], np.uint8)
        B = IndexBuffer(data)
        assert B.dtype == np.uint8
        
        # We can also convert
        B.set_data(data, convert=True)
        assert B.dtype == np.uint32
        
        # Structured data not allowed
        self.assertRaises(TypeError, IndexBuffer, dtype=dtype)
        self.assertRaises(TypeError, B.set_data, sdata)


run_tests_if_main()
