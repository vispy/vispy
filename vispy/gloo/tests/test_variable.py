# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
import numpy as np

from vispy.gloo import gl
from vispy.gloo.variable import Uniform, Variable, Attribute


# -----------------------------------------------------------------------------
class VariableTest(unittest.TestCase):

    def test_init(self):
        variable = Variable(None, "A", gl.GL_FLOAT)
        assert variable._handle == -1
        assert variable.name == "A"
        assert variable.data is None
        assert variable.gtype == gl.GL_FLOAT
        assert variable.enabled is True

    def test_init_wrong_type(self):
        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_INT_VEC2)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_INT_VEC2)

        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_INT_VEC3)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_INT_VEC3)

        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_INT_VEC4)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_INT_VEC4)

        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_BOOL_VEC2)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_BOOL_VEC2)

        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_BOOL_VEC3)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_BOOL_VEC3)

        # with self.assertRaises(TypeError):
        #    v = Variable(None, "A", gl.GL_BOOL_VEC4)
        self.assertRaises(TypeError, Variable, None, "A", gl.GL_BOOL_VEC4)


# -----------------------------------------------------------------------------
class UniformTest(unittest.TestCase):

    def test_init(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT)
        assert uniform._unit == -1

    def test_float(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 1

    def test_vec2(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_VEC2)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 2

    def test_vec3(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_VEC2)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 2

    def test_vec4(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_VEC2)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 2

    def test_int(self):
        uniform = Uniform(None, "A", gl.GL_INT)
        assert uniform.data.dtype == np.int32
        assert uniform.data.size == 1

    def test_mat2(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_MAT2)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 4

    def test_mat3(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_MAT3)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 9

    def test_mat4(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_MAT4)
        assert uniform.data.dtype == np.float32
        assert uniform.data.size == 16

    def test_set(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_VEC4)

        uniform.set_data(1)
        assert (uniform.data == 1).all()

        uniform.set_data([1, 2, 3, 4])
        assert (uniform.data == [1, 2, 3, 4]).all()

    def test_set_exception(self):
        uniform = Uniform(None, "A", gl.GL_FLOAT_VEC4)

        # with self.assertRaises(ValueError):
        #    uniform.set_data([1, 2])
        self.assertRaises(ValueError, uniform.set_data, [1, 2])

        # with self.assertRaises(ValueError):
        #    uniform.set_data([1, 2, 3, 4, 5])
        self.assertRaises(ValueError, uniform.set_data, [1, 2, 3, 4, 5])


# -----------------------------------------------------------------------------
class AttributeTest(unittest.TestCase):

    def test_init(self):
        attribute = Attribute(None, "A", gl.GL_FLOAT)
        assert attribute.size == 0

    def test_set_generic(self):
        attribute = Attribute(None, "A", gl.GL_FLOAT_VEC4)

        attribute.set_data(1)
        assert type(attribute.data) is np.ndarray

#    @unittest.expectedFailure
#    def test_set_generic_2(self):
#        attribute = Attribute(None, "A", gl.GL_FLOAT_VEC4)
#        attribute.set_data([1, 2, 3, 4])
#        assert type(attribute.data) is np.ndarray


if __name__ == "__main__":
    unittest.main()
