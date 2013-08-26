# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import OpenGL.GL as gl

from vispy.oogl.shader import VertexShader
from vispy.oogl.shader import FragmentShader
from vispy.oogl.shader import ShaderException



# -----------------------------------------------------------------------------
class VertexShaderTest(unittest.TestCase):

    def test_init(self):
        shader = VertexShader()
        assert shader.type == gl.GL_VERTEX_SHADER

# -----------------------------------------------------------------------------
class FragmentShaderTest(unittest.TestCase):

    def test_init(self):
        shader = FragmentShader()
        assert shader.type == gl.GL_FRAGMENT_SHADER


# -----------------------------------------------------------------------------
class ShaderTest(unittest.TestCase):

    def test_init(self):
        shader = VertexShader()
        assert shader._handle == 0
        assert shader.dirty   == True
        assert shader.status  == False
        assert shader.code    == None
        assert shader.source  == None

    def test_sourcecode(self):
        code = "/* Code */"
        shader = VertexShader(code)
        assert shader.code == code
        assert shader.source == "<string>"

    def test_setcode(self):
        shader = VertexShader()
        shader._dirty = False
        shader.code = ""
        assert shader.dirty == True

    def test_empty_build(self):
        shader = VertexShader()
        with self.assertRaises(ShaderException):
            shader.build()

    def test_delete_no_context(self):
        shader = VertexShader()
        shader.delete()

    def test_uniform_float(self):
        shader = VertexShader("uniform float color;")
        assert shader.uniforms == [ ("color", gl.GL_FLOAT) ]

    def test_uniform_vec4(self):
        shader = VertexShader("uniform vec4 color;")
        assert shader.uniforms == [ ("color", gl.GL_FLOAT_VEC4) ]

    def test_uniform_array(self):
        shader = VertexShader("uniform float color[2];")
        assert shader.uniforms == [ ("color[0]", gl.GL_FLOAT),
                                    ("color[1]", gl.GL_FLOAT)  ]

    def test_attribute_float(self):
        shader = VertexShader("attribute float color;")
        assert shader.attributes == [ ("color", gl.GL_FLOAT) ]

    def test_attribute_vec4(self):
        shader = VertexShader("attribute vec4 color;")
        assert shader.attributes == [ ("color", gl.GL_FLOAT_VEC4) ]

if __name__ == "__main__":
    unittest.main()
