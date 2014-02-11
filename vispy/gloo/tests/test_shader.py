# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
from vispy.gloo import gl

from vispy.gloo.shader import VertexShader
from vispy.gloo.shader import FragmentShader


# -----------------------------------------------------------------------------
class VertexShaderTest(unittest.TestCase):

    def test_init(self):
        shader = VertexShader()
        assert shader._target == gl.GL_VERTEX_SHADER

# -----------------------------------------------------------------------------


class FragmentShaderTest(unittest.TestCase):

    def test_init(self):
        shader = FragmentShader()
        assert shader._target == gl.GL_FRAGMENT_SHADER


# -----------------------------------------------------------------------------
class ShaderTest(unittest.TestCase):

    def test_init(self):
        shader = VertexShader()
        assert shader._handle == 0
        assert shader._need_update is False
        assert shader._valid is False
        assert shader.code is None
        assert shader.source is None

    def test_sourcecode(self):
        code = "/* Code */"
        shader = VertexShader(code)
        assert shader.code == code
        assert shader.source == "<string>"

    def test_setcode(self):
        shader = VertexShader()
        shader.set_code("")
        assert shader._need_update

    def test_empty_build(self):
        shader = VertexShader()
        assert shader._code is None
        # This needs a context, because _init() will be called first
        # with self.assertRaises(ShaderError):
        #    shader.activate()

    def test_delete_no_context(self):
        shader = VertexShader()
        shader.delete()

    def test_uniform_float(self):
        shader = VertexShader("uniform float color;")
        uniforms = shader._get_uniforms()
        assert uniforms == [("color", gl.GL_FLOAT)]

    def test_uniform_vec4(self):
        shader = VertexShader("uniform vec4 color;")
        uniforms = shader._get_uniforms()
        assert uniforms == [("color", gl.GL_FLOAT_VEC4)]

    def test_uniform_array(self):
        shader = VertexShader("uniform float color[2];")
        uniforms = shader._get_uniforms()
        assert uniforms == [("color[0]", gl.GL_FLOAT),
                            ("color[1]", gl.GL_FLOAT)]

    def test_attribute_float(self):
        shader = VertexShader("attribute float color;")
        attributes = shader._get_attributes()
        assert attributes == [("color", gl.GL_FLOAT)]

    def test_attribute_vec4(self):
        shader = VertexShader("attribute vec4 color;")
        attributes = shader._get_attributes()
        assert attributes == [("color", gl.GL_FLOAT_VEC4)]
