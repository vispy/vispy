# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
from vispy import gl

from vispy.oogl.shader import VertexShader
from vispy.oogl.shader import FragmentShader
from vispy.oogl.shader import ShaderException



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
        assert shader._need_update == False
        assert shader._valid == False
        assert shader.code    == None
        assert shader.source  == None

    def test_sourcecode(self):
        code = "/* Code */"
        shader = VertexShader(code)
        assert shader.code == code
        assert shader.source == "<string>"

    def test_setcode(self):
        shader = VertexShader()
        shader.set_code("")
        assert shader._need_update == True

    def test_empty_build(self):
        shader = VertexShader()
        with self.assertRaises(RuntimeError):
            shader.activate()

    def test_delete_no_context(self):
        shader = VertexShader()
        shader.delete()

    def test_uniform_float(self):
        shader = VertexShader("uniform float color;")
        uniforms = shader._get_uniforms()
        assert uniforms == [ ("color", gl.GL_FLOAT) ]
 
    def test_uniform_vec4(self):
        shader = VertexShader("uniform vec4 color;")
        uniforms = shader._get_uniforms()
        assert uniforms == [ ("color", gl.GL_FLOAT_VEC4) ]
 
    def test_uniform_array(self):
        shader = VertexShader("uniform float color[2];")
        uniforms=shader._get_uniforms()
        assert uniforms == [ ("color[0]", gl.GL_FLOAT),
                             ("color[1]", gl.GL_FLOAT)  ]
 
    def test_attribute_float(self):
        shader = VertexShader("attribute float color;")
        attributes = shader._get_attributes()
        assert attributes == [ ("color", gl.GL_FLOAT) ]
 
    def test_attribute_vec4(self):
        shader = VertexShader("attribute vec4 color;")
        attributes = shader._get_attributes()
        assert attributes == [ ("color", gl.GL_FLOAT_VEC4) ]

if __name__ == "__main__":
    unittest.main()
