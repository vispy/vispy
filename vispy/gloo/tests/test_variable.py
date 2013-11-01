# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from vispy.gloo import gl

from vispy.gloo.variable import Uniform
from vispy.gloo.variable import Variable
from vispy.gloo.variable import Attribute


# -----------------------------------------------------------------------------
class VariableTest(unittest.TestCase):

    def test_init(self):
        variable = Variable("A", gl.GL_FLOAT)
        assert variable._dirty == False
        assert variable.name    == "A"
        assert variable.data    is None
        assert variable.gtype   == gl.GL_FLOAT
        assert variable.active  == False


    def test_init_wrong_type(self):
        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_INT_VEC2)
        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_INT_VEC3)
        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_INT_VEC4)

        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_BOOL_VEC2)
        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_BOOL_VEC3)
        with self.assertRaises(ValueError):
            v = Variable("A", gl.GL_BOOL_VEC4)



# -----------------------------------------------------------------------------
class UniformTest(unittest.TestCase):

    def test_init(self):
        uniform = Uniform("A", gl.GL_FLOAT)
        assert uniform.texture_unit == -1

    def test_float(self):
        uniform = Uniform("A", gl.GL_FLOAT)
        assert uniform.dtype == np.float32
        assert uniform.size == 1

    def test_vec2(self):
        uniform = Uniform("A", gl.GL_FLOAT_VEC2)
        assert uniform.dtype == np.float32
        assert uniform.size == 2

    def test_vec3(self):
        uniform = Uniform("A", gl.GL_FLOAT_VEC2)
        assert uniform.dtype == np.float32
        assert uniform.size == 2

    def test_vec4(self):
        uniform = Uniform("A", gl.GL_FLOAT_VEC2)
        assert uniform.dtype == np.float32
        assert uniform.size == 2

    def test_int(self):
        uniform = Uniform("A", gl.GL_INT)
        assert uniform.dtype == np.int32
        assert uniform.size == 1

    def test_mat2(self):
        uniform = Uniform("A", gl.GL_FLOAT_MAT2)
        assert uniform.dtype == np.float32
        assert uniform.size == 4

    def test_mat3(self):
        uniform = Uniform("A", gl.GL_FLOAT_MAT3)
        assert uniform.dtype == np.float32
        assert uniform.size == 9

    def test_mat4(self):
        uniform = Uniform("A", gl.GL_FLOAT_MAT4)
        assert uniform.dtype == np.float32
        assert uniform.size == 16

    def test_set(self):
        uniform = Uniform("A", gl.GL_FLOAT_VEC4)

        uniform.set_data(1)
        assert (uniform.data == 1).all()

        uniform.set_data([1,2,3,4])
        assert (uniform.data == [1,2,3,4]).all()

    def test_set_exception(self):
        uniform = Uniform("A", gl.GL_FLOAT_VEC4)

        with self.assertRaises(ValueError):
            uniform.set_data([1,2])

        with self.assertRaises(ValueError):
            uniform.set_data([1,2,3,4,5])


# -----------------------------------------------------------------------------
class AttributeTest(unittest.TestCase):

    def test_init(self):
        attribute = Attribute("A", gl.GL_FLOAT)
        assert attribute.size == 1

    def test_set_generic(self):
        attribute = Attribute("A", gl.GL_FLOAT_VEC4)

        attribute.set_data([1,2,3,4])
        assert type(attribute.data) is np.ndarray

        attribute.set_data(1)
        assert type(attribute.data) is np.ndarray


if __name__ == "__main__":
    unittest.main()
