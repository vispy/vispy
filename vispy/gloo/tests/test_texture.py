# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.gloo.texture import Texture, Texture1D, Texture2D, Texture3D
from vispy.gloo import gl
from vispy.testing import requires_pyopengl


# ----------------------------------------------------------------- Texture ---
class TextureTest(unittest.TestCase):

    # No data, no dtype : forbidden
    # ---------------------------------
    def test_init_none(self):
        # with self.assertRaises(ValueError):
        #    T = Texture()
        self.assertRaises(ValueError, Texture)

    # Data only
    # ---------------------------------
    def test_init_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        assert T._shape == (10, 10)
        assert T._dtype == np.uint8
        assert T._offset == (0, 0)
        assert T._store is True
        assert T._copy is False
        assert T._need_resize is True
        assert T._data is data
        assert len(T._pending_data) == 1

    # Non contiguous data
    # ---------------------------------
    def test_init_non_contiguous_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data[::2, ::2])
        assert T._shape == (5, 5)
        assert T._dtype == np.uint8
        assert T._offset == (0, 0)
        assert T._store is True
        assert T._copy is True
        assert T._need_resize is True
        assert T._pending_data
        assert T._data is not data
        assert len(T._pending_data) == 1

    # Dtype and shape
    # ---------------------------------
    def test_init_dtype_shape(self):
        T = Texture(shape=(10, 10), dtype=np.uint8)
        assert T._shape == (10, 10)
        assert T._dtype == np.uint8
        assert T._offset == (0, 0)
        assert T._store is True
        assert T._copy is False
        assert T._need_resize is True
        assert not T._pending_data
        assert T._data is not None
        assert T._data.shape == (10, 10)
        assert T._data.dtype == np.uint8
        assert len(T._pending_data) == 0

    # Dtype only
    # ---------------------------------
    def test_init_dtype(self):
        T = Texture(dtype=np.uint8)
        assert T._shape == ()
        assert T._dtype == np.uint8
        assert T._offset == ()
        assert T._store is True
        assert T._copy is False
        assert T._need_resize is False
        assert not T._pending_data
        assert T._data is not None
        assert len(T._pending_data) == 0

    # Data and dtype: dtype prevails
    # ---------------------------------
    def test_init_data_dtype(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data, dtype=np.uint16)
        assert T._shape == (10, 10)
        assert T._dtype == np.uint16
        assert T._offset == (0, 0)
        assert T._store is True
        assert T._copy is False
        assert T._need_resize is True
        assert T._data is not data
        assert T._pending_data
        assert len(T._pending_data) == 1

    # Data, store but no copy
    # ---------------------------------
    def test_init_data_store(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data, store=True)
        assert T._data is data

    # Data, store and copy
    # ---------------------------------
    def test_init_data_store_copy(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data.copy(), store=True)
        assert T._data is not data
        assert T._data is not None

    # Get a view of the whole texture
    # ---------------------------------
    def test_getitem_ellipsis(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[...]
        assert Z._base is T
        assert Z._data.base is T._data
        assert Z._shape == (10, 10)
        assert Z._resizeable is False
        assert len(Z._pending_data) == 0

    # Get a view using ellipsis at start
    # ---------------------------------
    def test_getitem_ellipsis_start(self):

        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[..., 0]
        assert Z._base is T
        assert Z._data.base is T._data
        assert Z._shape == (10, 10, 1)
        assert Z._resizeable is False
        assert len(Z._pending_data) == 0

    # Get a view using ellipsis at end
    # ---------------------------------
    def test_getitem_ellipsis_end(self):

        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[0, ...]
        assert Z._base is T
        assert Z._data.base is T._data
        assert Z._shape == (1, 10, 10)
        assert Z._resizeable is False
        assert len(Z._pending_data) == 0

    # Get a single item
    # ---------------------------------
    def test_getitem_single(self):

        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[0, 0, 0]
        assert Z._base is T
        assert Z._data.base is T._data
        assert Z._shape == (1, 1, 1)
        assert Z._resizeable is False
        assert len(Z._pending_data) == 0

    # Get a partial view
    # ---------------------------------
    def test_getitem_partial(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[2:5, 2:5]
        assert Z._base is T
        assert Z._data.base is T._data
        assert Z._shape == (3, 3)
        assert Z._offset == (2, 2)
        assert Z._resizeable is False
        assert len(Z._pending_data) == 0

    # Get non contiguous view : forbidden
    # ---------------------------------
    def test_getitem_non_contiguous(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        # with self.assertRaises(ValueError):
        #    Z = T[::2, ::2]
        #    print(Z)
        s = slice(None, None, 2)
        self.assertRaises(ValueError, T.__getitem__, (s, s))

    # Set data with store
    # ---------------------------------
    def test_setitem_all(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[...] = np.ones((10, 10))
        assert len(T._pending_data) == 1
        assert np.allclose(data, np.ones((10, 10)))

    # Set data without store
    # ---------------------------------
    def test_setitem_all_no_store(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data, store=False)
        T[...] = np.ones((10, 10), np.uint8)
        assert len(T._pending_data) == 1
        assert np.allclose(data, np.zeros((10, 10)))

    # Set a single data
    # ---------------------------------
    def test_setitem_single(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[0, 0] = 1
        assert len(T._pending_data) == 2
        assert data[0, 0] == 1, 1

    # Set some data
    # ---------------------------------
    def test_setitem_partial(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[5:, 5:] = 1
        assert len(T._pending_data) == 2
        assert np.allclose(data[5:, 5:], np.ones((5, 5)))

    # Set non contiguous data
    # ---------------------------------
    def test_setitem_wrong(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        # with self.assertRaises(ValueError):
        #    T[::2, ::2] = 1
        s = slice(None, None, 2)
        self.assertRaises(ValueError, T.__setitem__, (s, s), 1)

    # Set via get (pending data on base)
    # ---------------------------------
    def test_getitem_setitem(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        Z = T[5:, 5:]
        Z[...] = 1
        assert len(Z._pending_data) == 0
        assert len(T._pending_data) == 2
        assert np.allclose(data[5:, 5:], np.ones((5, 5)))


# --------------------------------------------------------------- Texture1D ---
class Texture1DTest(unittest.TestCase):
    
    # Shape extension
    # ---------------------------------
    def test_init(self):
        data = np.zeros(10, dtype=np.uint8)
        T = Texture1D(data=data)
        assert T._shape == (10, 1)

    # Width
    # ---------------------------------
    def test_width(self):
        data = np.zeros(10, dtype=np.uint8)
        T = Texture1D(data=data)
        assert T.width == 10

    # Set misshaped data
    # ---------------------------------
    def test_set_misshaped_data_1D(self):
        data = np.zeros(10, dtype=np.uint8)
        T = Texture1D(data=data)
        # with self.assertRaises(ValueError):
        #    T.set_data(np.ones((10, 10)))
        self.assertRaises(ValueError, T.set_data, np.ones((10, 10)))


# --------------------------------------------------------------- Texture2D ---
class Texture2DTest(unittest.TestCase):
    # Note: put many tests related to (re)sizing here, because Texture
    # is not really aware of shape.
    
    # Shape extension
    # ---------------------------------
    def test_init(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        assert T._shape == (10, 10, 1)

    # Width & height
    # ---------------------------------
    def test_width_height(self):
        data = np.zeros((10, 20), dtype=np.uint8)
        T = Texture2D(data=data)
        assert T.width == 20
        assert T.height == 10
    
    # Resize
    # ---------------------------------
    def test_resize(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.resize((5, 5))
        assert T.shape == (5, 5, 1)
        assert T._data.shape == (5, 5, 1)
        assert T._need_resize is True
        assert not T._pending_data
        assert len(T._pending_data) == 0

    # Resize with bad shape
    # ---------------------------------
    def test_resize_bad_shape(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        # with self.assertRaises(ValueError):
        #    T.resize((5, 5, 5))
        self.assertRaises(ValueError, T.resize, (5, 5, 5))

    # Resize view (forbidden)
    # ---------------------------------
    def test_resize_view(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        # with self.assertRaises(RuntimeError):
        #    T[...].resize((5, 5))
        Z = T[...]
        self.assertRaises(RuntimeError, Z.resize, (5, 5))

    # Resize not resizeable
    # ---------------------------------
    def test_resize_unresizeable(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data, resizeable=False)
        # with self.assertRaises(RuntimeError):
        #    T.resize((5, 5))
        self.assertRaises(RuntimeError, T.resize, (5, 5))
    
    # Set oversized data (-> resize)
    # ---------------------------------
    def test_set_oversized_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.set_data(np.ones((20, 20), np.uint8))
        assert T.shape == (20, 20, 1)
        assert T._data.shape == (20, 20, 1)
        assert len(T._pending_data) == 1
    
    # Set undersized data
    # ---------------------------------
    def test_set_undersized_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.set_data(np.ones((5, 5), np.uint8))
        assert T.shape == (5, 5, 1)
        assert len(T._pending_data) == 1

    # Set misplaced data
    # ---------------------------------
    def test_set_misplaced_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        # with self.assertRaises(ValueError):
        #    T.set_data(np.ones((5, 5)), offset=(8, 8))
        self.assertRaises(ValueError, T.set_data,
                          np.ones((5, 5)), offset=(8, 8))

    # Set misshaped data
    # ---------------------------------
    def test_set_misshaped_data_2D(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        # with self.assertRaises(ValueError):
        #    T.set_data(np.ones((10, 10)))
        self.assertRaises(ValueError, T.set_data, np.ones((10,)))

    # Set whole data (clear pending data)
    # ---------------------------------
    def test_set_whole_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.set_data(np.ones((10, 10), np.uint8))
        assert T.shape == (10, 10, 1)
        assert len(T._pending_data) == 1
    
    # Test view get invalidated when base is resized
    # ----------------------------------------------
    def test_invalid_views(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        Z = T[5:, 5:]
        T.resize((5, 5))
        assert Z._valid is False
    
    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_shape(self):
        shape1 = 10, 10
        shape3 = 10, 10, 3
        
        # Init data (explicit shape)
        data = np.zeros((10, 10, 1), dtype=np.uint8)
        T = Texture2D(data=data)
        assert T.shape == (10, 10, 1)
        assert T._format == gl.GL_LUMINANCE
        
        # Set data to rgb
        T.set_data(np.zeros(shape3, np.uint8))
        assert T.shape == (10, 10, 3)
        assert T._format == gl.GL_RGB
        
        # Set data to grayscale
        T.set_data(np.zeros(shape1, np.uint8))
        assert T.shape == (10, 10, 1)
        assert T._format == gl.GL_LUMINANCE
        
        # Set size to rgb
        T.resize(shape3)
        assert T.shape == (10, 10, 3)
        assert T._format == gl.GL_RGB
        
        # Set size to grayscale
        T.resize(shape1)
        assert T.shape == (10, 10, 1)
        assert T._format == gl.GL_LUMINANCE
    
    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_type(self):
        shape = 10, 10
        T = Texture2D(data=np.zeros(shape, dtype=np.uint8))
        assert T.dtype == np.uint8
        assert T._gtype == gl.GL_UNSIGNED_BYTE
        
        newdata = np.zeros(shape, dtype=np.float32)
        self.assertRaises(ValueError, T.set_data, newdata)
        
        newdata = np.zeros(shape, dtype=np.int32)
        self.assertRaises(ValueError, T.set_data, newdata)


# --------------------------------------------------------------- Texture3D ---
class Texture3DTest(unittest.TestCase):
    # Note: put many tests related to (re)sizing here, because Texture
    # is not really aware of shape.

    @requires_pyopengl()
    def __init__(self, *args, **kwds):
        unittest.TestCase.__init__(self, *args, **kwds)

    # Shape extension
    # ---------------------------------
    def test_init(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        assert T._shape == (10, 10, 10, 1)

    # Width & height
    # ---------------------------------
    def test_width_height_depth(self):
        data = np.zeros((10, 20, 30), dtype=np.uint8)
        T = Texture3D(data=data)
        assert T.width == 20
        assert T.height == 10
        assert T.depth == 30

    # Resize
    # ---------------------------------
    def test_resize(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.resize((5, 5, 5))
        assert T.shape == (5, 5, 5, 1)
        assert T._data.shape == (5, 5, 5, 1)
        assert T._need_resize is True
        assert not T._pending_data
        assert len(T._pending_data) == 0

    # Resize with bad shape
    # ---------------------------------
    def test_resize_bad_shape(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        # with self.assertRaises(ValueError):
        #    T.resize((5, 5, 5, 5))
        self.assertRaises(ValueError, T.resize, (5, 5, 5, 5))

    # Resize not resizeable
    # ---------------------------------
    def test_resize_unresizeable(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data, resizeable=False)
        # with self.assertRaises(RuntimeError):
        #    T.resize((5, 5, 5))
        self.assertRaises(RuntimeError, T.resize, (5, 5, 5))

    # Set oversized data (-> resize)
    # ---------------------------------
    def test_set_oversized_data(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.set_data(np.ones((20, 20, 20), np.uint8))
        assert T.shape == (20, 20, 20, 1)
        assert T._data.shape == (20, 20, 20, 1)
        assert len(T._pending_data) == 1

    # Set undersized data
    # ---------------------------------
    def test_set_undersized_data(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.set_data(np.ones((5, 5, 5), np.uint8))
        assert T.shape == (5, 5, 5, 1)
        assert len(T._pending_data) == 1

    # Set misplaced data
    # ---------------------------------
    def test_set_misplaced_data(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        # with self.assertRaises(ValueError):
        #    T.set_data(np.ones((5, 5, 5)), offset=(8, 8, 8))
        self.assertRaises(ValueError, T.set_data,
                          np.ones((5, 5, 5)), offset=(8, 8, 8))

    # Set misshaped data
    # ---------------------------------
    def test_set_misshaped_data_3D(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        # with self.assertRaises(ValueError):
        #    T.set_data(np.ones((10, 10, 10)))
        self.assertRaises(ValueError, T.set_data, np.ones((10,)))

    # Set whole data (clear pending data)
    # ---------------------------------
    def test_set_whole_data(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.set_data(np.ones((10, 10, 10), np.uint8))
        assert T.shape == (10, 10, 10, 1)
        assert len(T._pending_data) == 1

    # Test view get invalidated when base is resized
    # ----------------------------------------------
    def test_invalid_views(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        Z = T[5:, 5:, 5:]
        T.resize((5, 5, 5))
        assert Z._valid is False

    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_shape(self):
        shape1 = 10, 10, 10
        shape3 = 10, 10, 10, 3
        
        # Init data (explicit shape)
        data = np.zeros((10, 10, 10, 1), dtype=np.uint8)
        T = Texture3D(data=data)
        assert T.shape == (10, 10, 10, 1)
        assert T._format == gl.GL_LUMINANCE
        
        # Set data to rgb
        T.set_data(np.zeros(shape3, np.uint8))
        assert T.shape == (10, 10, 10, 3)
        assert T._format == gl.GL_RGB
        
        # Set data to grayscale
        T.set_data(np.zeros(shape1, np.uint8))
        assert T.shape == (10, 10, 10, 1)
        assert T._format == gl.GL_LUMINANCE
        
        # Set size to rgb
        T.resize(shape3)
        assert T.shape == (10, 10, 10, 3)
        assert T._format == gl.GL_RGB
        
        # Set size to grayscale
        T.resize(shape1)
        assert T.shape == (10, 10, 10, 1)
        assert T._format == gl.GL_LUMINANCE

    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_type(self):
        shape = 10, 10, 10
        T = Texture3D(data=np.zeros(shape, dtype=np.uint8))
        assert T.dtype == np.uint8
        assert T._gtype == gl.GL_UNSIGNED_BYTE
        
        newdata = np.zeros(shape, dtype=np.float32)
        self.assertRaises(ValueError, T.set_data, newdata)
        
        newdata = np.zeros(shape, dtype=np.int32)
        self.assertRaises(ValueError, T.set_data, newdata)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
