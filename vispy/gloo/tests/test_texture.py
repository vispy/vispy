# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.gloo import Texture1D, Texture2D, Texture3D, gl
from vispy.testing import requires_pyopengl


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
