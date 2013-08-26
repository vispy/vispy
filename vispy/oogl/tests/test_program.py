# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import OpenGL.GL as gl

from vispy.oogl.program import Program
from vispy.oogl.shader import VertexShader
from vispy.oogl.shader import FragmentShader
from vispy.oogl.program import ProgramException




# -----------------------------------------------------------------------------
class ProgramTest(unittest.TestCase):

    def test_init(self):
        program = Program()
        assert program._handle == 0
        assert program.dirty   == True
        assert program.status  == False
        assert program.shaders == []

    def test_delete_no_context(self):
        program = Program()
        program.delete()

    def test_init_from_string(self):
        program = Program("A","B")
        assert len(program.shaders) == 2
        assert program.shaders[0].code == "A"
        assert program.shaders[1].code == "B"

    def test_init_from_shader(self):
        program = Program(VertexShader("A"),FragmentShader("B"))
        assert len(program.shaders) == 2
        assert program.shaders[0].code == "A"
        assert program.shaders[1].code == "B"

    def test_unique_shader(self):
        vert = VertexShader("A")
        frag = FragmentShader("B")
        program = Program([vert,vert],[frag,frag,frag])
        assert len(program.shaders) == 2

    def test_uniform(self):
        vert = VertexShader("uniform float A;")
        frag = FragmentShader("uniform float A; uniform vec4 B;")
        program = Program(vert,frag)
        assert program.all_uniforms == [ ("A", gl.GL_FLOAT),
                                         ("B", gl.GL_FLOAT_VEC4) ]

    def test_attributes(self):
        vert = VertexShader("attribute float A;")
        frag = FragmentShader("")
        program = Program(vert,frag)
        assert program.all_attributes == [ ("A", gl.GL_FLOAT) ]

    def test_attach(self):
        vert = VertexShader("A")
        frag = FragmentShader("B")
        program = Program(vert)
        program.attach(frag)
        assert len(program.shaders) == 2
        assert program.shaders[0].code == "A"
        assert program.shaders[1].code == "B"

    def test_detach(self):
        vert = VertexShader("A")
        frag = FragmentShader("B")
        program = Program(vert, frag)
        program.detach(frag)
        assert len(program.shaders) == 1
        assert program.shaders[0].code == "A"

    def test_failed_build(self):
        vert = VertexShader("A")
        frag = FragmentShader("B")

        program = Program(verts = vert)
        with self.assertRaises(ProgramException):
            program.build()

        program = Program(frags = frag)
        with self.assertRaises(ProgramException):
            program.build()

    def test_setitem(self):
        vert = VertexShader("")
        frag = FragmentShader("")

        program = Program(vert,frag)
        with self.assertRaises(ProgramException):
            program["A"] = 1



if __name__ == "__main__":
    unittest.main()
