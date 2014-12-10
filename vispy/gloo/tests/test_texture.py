# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.gloo import Texture2D, Texture3D, TextureAtlas
from vispy.testing import requires_pyopengl, run_tests_if_main

# here we test some things that will be true of all Texture types:
Texture = Texture2D


# ----------------------------------------------------------------- Texture ---
class TextureTest(unittest.TestCase):

    # No data, no dtype : forbidden
    # ---------------------------------
    def test_init_none(self):
        self.assertRaises(ValueError, Texture)

    # Data only
    # ---------------------------------
    def test_init_data(self):
        data = np.zeros((10, 10, 3), dtype=np.uint8)
        T = Texture(data=data, interpolation='linear', wrapping='repeat')
        assert T._shape == (10, 10, 3)
        assert T._interpolation == ('linear', 'linear')
        assert T._wrapping == ('repeat', 'repeat')

    # Setting data and shape
    # ---------------------------------
    def test_init_dtype_shape(self):
        T = Texture((10, 10))
        assert T._shape == (10, 10, 1)
        self.assertRaises(ValueError, Texture, shape=(10, 10),
                          data=np.zeros((10, 10), np.float32))

    # Set data with store
    # ---------------------------------
    def test_setitem_all(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[...] = np.ones((10, 10, 1))
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'DATA'
        assert np.allclose(glir_cmd[3], np.ones((10, 10, 1)))

    # Set data without store
    # ---------------------------------
    def test_setitem_all_no_store(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[...] = np.ones((10, 10), np.uint8)
        assert np.allclose(data, np.zeros((10, 10)))

    # Set a single data
    # ---------------------------------
    def test_setitem_single(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[0, 0, 0] = 1
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'DATA'
        assert np.allclose(glir_cmd[3], np.array([1]))
        
        # We apparently support this
        T[8:3, 3] = 1

    # Set some data
    # ---------------------------------
    def test_setitem_partial(self):

        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        T[5:, 5:] = 1
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'DATA'
        assert np.allclose(glir_cmd[3], np.ones((5, 5)))

    # Set non contiguous data
    # ---------------------------------
    def test_setitem_wrong(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture(data=data)
        # with self.assertRaises(ValueError):
        #    T[::2, ::2] = 1
        s = slice(None, None, 2)
        self.assertRaises(IndexError, T.__setitem__, (s, s), 1)
        self.assertRaises(IndexError, T.__setitem__, (-100, 3), 1)
        self.assertRaises(TypeError, T.__setitem__, ('foo', 'bar'), 1)

    # Set properties
    def test_set_texture_properties(self):
        T = Texture((10, 10))
        
        # Interpolation
        T.interpolation = 'nearest'
        assert T.interpolation == 'nearest'
        T.interpolation = 'linear'
        assert T.interpolation == 'linear'
        T.interpolation = ['linear'] * 2
        assert T.interpolation == 'linear'
        T.interpolation = ['linear', 'nearest']
        assert T.interpolation == ('linear', 'nearest')
        
        # Wrong interpolation
        iset = Texture.interpolation.fset
        self.assertRaises(ValueError, iset, T, ['linear'] * 3)
        self.assertRaises(ValueError, iset, T, True)
        self.assertRaises(ValueError, iset, T, [])
        self.assertRaises(ValueError, iset, T, 'linearios')
        
        # Wrapping
        T.wrapping = 'clamp_to_edge'
        assert T.wrapping == 'clamp_to_edge'
        T.wrapping = 'repeat'
        assert T.wrapping == 'repeat'
        T.wrapping = 'mirrored_repeat'
        assert T.wrapping == 'mirrored_repeat'
        T.wrapping = 'repeat', 'repeat'
        assert T.wrapping == 'repeat'
        T.wrapping = 'repeat', 'clamp_to_edge'
        assert T.wrapping == ('repeat', 'clamp_to_edge')
        
        # Wrong wrapping
        wset = Texture.wrapping.fset
        self.assertRaises(ValueError, wset, T, ['repeat'] * 3)
        self.assertRaises(ValueError, wset, T, True)
        self.assertRaises(ValueError, wset, T, [])
        self.assertRaises(ValueError, wset, T, 'repeatos')


# --------------------------------------------------------------- Texture2D ---
class Texture2DTest(unittest.TestCase):
    # Note: put many tests related to (re)sizing here, because Texture
    # is not really aware of shape.

    # Shape extension
    # ---------------------------------
    def test_init(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        assert 'Texture2D' in repr(T)
        assert T._shape == (10, 10, 1)
        assert T.glsl_type == ('uniform', 'sampler2D')

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
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'SIZE'
        
        # Wong arg
        self.assertRaises(ValueError, T.resize, (5, 5), 4)
    
    # Resize with bad shape
    # ---------------------------------
    def test_resize_bad_shape(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        # with self.assertRaises(ValueError):
        #    T.resize((5, 5, 5))
        self.assertRaises(ValueError, T.resize, (5,))
        self.assertRaises(ValueError, T.resize, (5, 5, 5))
        self.assertRaises(ValueError, T.resize, (5, 5, 5, 1))

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
        glir_cmds = T._glir.clear()
        assert glir_cmds[-2][0] == 'SIZE'
        assert glir_cmds[-1][0] == 'DATA'
    
    # Set undersized data
    # ---------------------------------
    def test_set_undersized_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.set_data(np.ones((5, 5), np.uint8))
        assert T.shape == (5, 5, 1)
        glir_cmds = T._glir.clear()
        assert glir_cmds[-2][0] == 'SIZE'
        assert glir_cmds[-1][0] == 'DATA'

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
        self.assertRaises(ValueError, T.set_data, np.ones((5, 5, 5, 1)),)
        
    # Set whole data (clear pending data)
    # ---------------------------------
    def test_set_whole_data(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        T.set_data(np.ones((10, 10), np.uint8))
        assert T.shape == (10, 10, 1)
    
    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_shape(self):
        shape1 = 10, 10
        shape3 = 10, 10, 3
        
        # Init data (explicit shape)
        data = np.zeros((10, 10, 1), dtype=np.uint8)
        T = Texture2D(data=data)
        assert T.shape == (10, 10, 1)
        assert T.format == 'luminance'
        
        # Set data to rgb
        T.set_data(np.zeros(shape3, np.uint8))
        assert T.shape == (10, 10, 3)
        assert T.format == 'rgb'
        
        # Set data to grayscale
        T.set_data(np.zeros(shape1, np.uint8))
        assert T.shape == (10, 10, 1)
        assert T.format == 'luminance'
        
        # Set size to rgb
        T.resize(shape3)
        assert T.shape == (10, 10, 3)
        assert T._format == 'rgb'
        
        # Set size to grayscale
        T.resize(shape1)
        assert T.shape == (10, 10, 1)
        assert T._format == 'luminance'
        
        # Keep using old format
        T.resize(shape1, 'alpha')
        T.resize(shape1)
        assert T._format == 'alpha'
        
        # Use luminance as default
        T.resize(shape3)
        T.resize(shape1)
        assert T._format == 'luminance'
        
        # Too large
        self.assertRaises(ValueError, T.resize, (5, 5, 5, 1))
        # Cannot determine format
        self.assertRaises(ValueError, T.resize, (5, 5, 5))
        # Invalid format
        self.assertRaises(ValueError, T.resize, shape3, 'foo')
        self.assertRaises(ValueError, T.resize, shape3, 'alpha')
        #self.assertRaises(ValueError, T.resize, shape3, 4)
    
    # Test set data with different shape and type
    # -------------------------------------------
    def test_reset_data_type(self):
        data = np.zeros((10, 10), dtype=np.uint8)
        T = Texture2D(data=data)
        
        data = np.zeros((10, 11), dtype=np.float32)
        T.set_data(data)
        
        data = np.zeros((12, 10), dtype=np.int32)
        T.set_data(data)
        
        self.assertRaises(ValueError, T.set_data, np.zeros([10, 10, 10, 1]))


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
        assert 'Texture3D' in repr(T)
        assert T.glsl_type == ('uniform', 'sampler3D')
        
    # Width & height
    # ---------------------------------
    def test_width_height_depth(self):
        data = np.zeros((10, 20, 30), dtype=np.uint8)
        T = Texture3D(data=data)
        assert T.width == 30
        assert T.height == 20
        assert T.depth == 10

    # Resize
    # ---------------------------------
    def test_resize(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.resize((5, 5, 5))
        assert T.shape == (5, 5, 5, 1)
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'SIZE'
        assert glir_cmd[2] == (5, 5, 5, 1)
    
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
        
    # Set undersized data
    # ---------------------------------
    def test_set_undersized_data(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        T.set_data(np.ones((5, 5, 5), np.uint8))
        assert T.shape == (5, 5, 5, 1)

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
        glir_cmd = T._glir.clear()[-1]
        assert glir_cmd[0] == 'DATA'

    # Test set data with different shape
    # ---------------------------------
    def test_reset_data_shape(self):
        shape1 = 10, 10, 10
        shape3 = 10, 10, 10, 3
        
        # Init data (explicit shape)
        data = np.zeros((10, 10, 10, 1), dtype=np.uint8)
        T = Texture3D(data=data)
        assert T.shape == (10, 10, 10, 1)
        assert T._format == 'luminance'
        
        # Set data to rgb
        T.set_data(np.zeros(shape3, np.uint8))
        assert T.shape == (10, 10, 10, 3)
        assert T._format == 'rgb'
        
        # Set data to grayscale
        T.set_data(np.zeros(shape1, np.uint8))
        assert T.shape == (10, 10, 10, 1)
        assert T._format == 'luminance'
        
        # Set size to rgb
        T.resize(shape3)
        assert T.shape == (10, 10, 10, 3)
        assert T._format == 'rgb'
        
        # Set size to grayscale
        T.resize(shape1)
        assert T.shape == (10, 10, 10, 1)
        assert T._format == 'luminance'

    # Test set data with different shape and type
    # -------------------------------------------
    def test_reset_data_type(self):
        data = np.zeros((10, 10, 10), dtype=np.uint8)
        T = Texture3D(data=data)
        
        data = np.zeros((10, 11, 11), dtype=np.float32)
        T.set_data(data)
        
        data = np.zeros((12, 12, 10), dtype=np.int32)
        T.set_data(data)


class TextureAtlasTest(unittest.TestCase):
    
    def test_init_atas(self):
        T = TextureAtlas((100, 100))
        assert T.shape == (128, 128, 3)  # rounds to powers of 2
        
        for i in [10, 20, 30, 40, 50, 60]:
            reg = T.get_free_region(10, 10)
            assert len(reg) == 4
        
        reg = T.get_free_region(129, 129)
        assert reg is None
    
    
run_tests_if_main()
