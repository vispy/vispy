# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.util import use_log_level
from vispy.gloo import gl
from vispy.gloo.buffer import Buffer, DataBuffer, VertexBuffer, IndexBuffer


# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    # Default init
    # ------------
    def test_init_default(self):
        B = Buffer()
        assert B._target == gl.GL_ARRAY_BUFFER
        assert B._handle == -1
        assert B._need_create is True
        assert B._need_delete is False
        assert B._nbytes == 0
        assert B._usage == gl.GL_DYNAMIC_DRAW

    # Unknown target
    # --------------
    def test_init_wrong_target(self):
        # with self.assertRaises(ValueError):
        #    B = Buffer(target=-1)
        self.assertRaises(ValueError, Buffer, target=-1)

    # No data
    # -------
    def test_init_no_data(self):
        B = Buffer()
        assert len(B._pending_data) == 0

    # Data
    # ----
    def test_init_with_data(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        assert len(B._pending_data) == 1

    # Check setting the whole buffer clear pending operations
    # -------------------------------------------------------
    def test_set_whole_data(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        B.set_data(data=data)
        assert len(B._pending_data) == 1

    # Check stored data is data
    # -------------------------
    def test_data_storage(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        B.set_data(data=data[:50], copy=False)
        assert B._pending_data[-1][0].base is data

    # Check stored data is a copy
    # ----------------------------
    def test_data_copy(self):
        data = np.zeros(100)
        B = Buffer(data=data)
        B.set_data(data=data[:50], copy=True)
        assert B._pending_data[-1][0].base is not data

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
        assert B._store is True
        assert B._copied is False
        assert B.nbytes == data.nbytes
        assert B.offset == 0
        assert B.size == 100
        assert B.itemsize == data.itemsize
        assert B.stride == data.itemsize
        assert B.dtype == data.dtype

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

    # CPU storage
    # ------------
    def test_storage(self):
        data = np.ones(100)
        B = DataBuffer(data, store=True)
        assert B.data.base is data

    # Use CPU storage but make a local copy for storage
    # -------------------------------------------------
    def test_storage_copy(self):
        data = np.ones(100, np.float32)
        B = DataBuffer(data.copy(), store=True)  # we got rid of copy arg
        assert B.data is not None
        assert B.data is not data
        assert B.stride == 4

    # No CPU storage
    # --------------
    def test_no_storage_copy(self):
        data = np.ones(100, np.float32)
        B = DataBuffer(data, store=False)
        assert B.data is None
        assert B.stride == 4

    # Empty init (not allowed)
    # ------------------------
    def test_empty_init(self):
        # with self.assertRaises(ValueError):
        #    B = DataBuffer()
        self.assertRaises(ValueError, DataBuffer)

    # Wrong storage
    # -------------
    def test_non_contiguous_storage(self):
        # Ask to have CPU storage and to use data as storage
        # Not possible since data[::2] is not contiguous
        data = np.ones(100, np.float32)
        data_given = data[::2]
        
        with use_log_level('warning', record=True, print_msg=False) as l:
            B = DataBuffer(data_given, store=True)
        assert len(l) == 1
        assert B._data is not data_given
        assert B.stride == 4
        
        B = DataBuffer(data_given, store=False)
        assert B._data is not data_given
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

    # Get item via index
    # ------------------
    def test_getitem_index(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        Z = B[0:1]
        assert Z.nbytes == 1 * (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.offset == 0
        assert Z.size == 1
        assert Z.itemsize == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.stride == (3 + 2 + 4) * np.dtype(np.float32).itemsize
        assert Z.dtype == B.dtype

    # View get invalidated when base is resized
    # -----------------------------------------
    def test_invalid_view_after_resize(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data)
        Z = B[5:]
        B.resize_bytes(5)
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
        B = DataBuffer(data, store=True)
        B.set_data(data)
        assert len(B._pending_data) == 1

    # Set data on view buffer : error
    # -------------------------------
    def test_set_data_base_view(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data, store=True)
        # set_data on field is not allowed because set_data
        # can result in a buffer resize

        # with self.assertRaises(ValueError):
        #    B['position'].set_data(data)
        Z = B['position']
        self.assertRaises(ValueError, Z.set_data, data)

    # Check set_data using offset in data buffer
    # ------------------------------------------
    def test_set_data_offset(self):
        data = np.zeros(100, np.float32)
        subdata = data[:10]
        
        B = DataBuffer(data)
        B.set_subdata(subdata, offset=10)
        offset = B._pending_data[-1][2]
        assert offset == 10*4

    # Setitem + broadcast
    # ------------------------------------------------------
    def test_setitem_broadcast(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data, store=True)
        B['position'] = 1, 2, 3
        assert np.allclose(data['position'].ravel(), np.resize([1, 2, 3], 30))

    # Setitem ellipsis
    # ------------------------------------------------------
    def test_setitem_ellipsis(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data1 = np.zeros(10, dtype=dtype)
        data2 = np.ones(10, dtype=dtype)
        B = DataBuffer(data1, store=True)
        B[...] = data2
        assert np.allclose(data1['position'], data2['position'])
        assert np.allclose(data1['texcoord'], data2['texcoord'])
        assert np.allclose(data1['color'], data2['color'])

    # Set every 2 item
    # ------------------------------------------------------
    def test_setitem_strided(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data1 = np.zeros(10, dtype=dtype)
        data2 = np.ones(10, dtype=dtype)
        B = DataBuffer(data1, store=True)
        B[::2] = data2[::2]
        assert np.allclose(data1['position'][::2], data2['position'][::2])
        assert np.allclose(data1['texcoord'][::2], data2['texcoord'][::2])
        assert np.allclose(data1['color'][::2], data2['color'][::2])

    # Set half the array
    # ------------------------------------------------------
    def test_setitem_half(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data1 = np.zeros(10, dtype=dtype)
        data2 = np.ones(10, dtype=dtype)
        B = DataBuffer(data1, store=True)
        B[:5] = data2[:5]
        assert np.allclose(data1['position'][:5], data2['position'][:5])
        assert np.allclose(data1['texcoord'][:5], data2['texcoord'][:5])
        assert np.allclose(data1['color'][:5], data2['color'][:5])
        assert len(B._pending_data) == 2

    # Set field without storage: error
    # --------------------------------
    def test_setitem_field_no_storage(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data, store=False)
        # with self.assertRaises(ValueError):
        #    B['position'] = 1, 2, 3
        self.assertRaises(ValueError,  B.__setitem__, 'position', (1, 2, 3))

    # Set every 2 item without storage:  error
    # ----------------------------------------
    def test_every_two_item_no_storage(self):
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color',    np.float32, 4)])
        data = np.zeros(10, dtype=dtype)
        B = DataBuffer(data, store=False)
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

    # Resize not allowed using ellipsis
    # --------------------------------
    def test_no_resize_ellipsis(self):
        data = np.zeros(10)
        B = DataBuffer(data=data)
        data = np.zeros(30)
        # with self.assertRaises(ValueError):
        #    B[...] = data
        self.assertRaises(ValueError, B.__setitem__, Ellipsis, data)


# -----------------------------------------------------------------------------
class VertexBufferTest(unittest.TestCase):

    # VertexBuffer allowed base types
    # -------------------------------
    def test_init_allowed_dtype(self):
        for dtype in (np.uint8, np.int8, np.uint16, np.int16, np.float32):
            V = VertexBuffer(dtype=dtype)
            names = V.dtype.names
            assert V.dtype[names[0]].base == dtype
            assert V.dtype[names[0]].shape == ()

    # VertexBuffer not allowed base types
    # -----------------------------------
    def test_init_not_allowed_dtype(self):
        for dtype in (np.uint32, np.int32, np.float64):
            # with self.assertRaises(TypeError):
            #    V = VertexBuffer(dtype=dtype)
            self.assertRaises(TypeError, VertexBuffer, dtype=dtype)

# -----------------------------------------------------------------------------


class IndexBufferTest(unittest.TestCase):

    # IndexBuffer allowed base types
    # ------------------------------
    def test_init_allowed_dtype(self):
        for dtype in (np.uint8, np.uint16, np.uint32):
            V = IndexBuffer(dtype=dtype)
            assert V.dtype == dtype

    # IndexBuffer not allowed base types
    # -----------------------------------
    def test_init_not_allowed_dtype(self):
        for dtype in (np.int8, np.int16, np.int32,
                      np.float16, np.float32, np.float64):
            # with self.assertRaises(TypeError):
            #    V = IndexBuffer(dtype=dtype)
            self.assertRaises(TypeError, IndexBuffer, dtype=dtype)

if __name__ == "__main__":
    unittest.main()
