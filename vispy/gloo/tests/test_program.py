# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from nose.tools import assert_raises

from vispy.gloo import gl
from vispy.gloo.program import Program
from vispy.gloo.shader import VertexShader, FragmentShader
from vispy.gloo.buffer import VertexBuffer, ClientVertexBuffer


# -----------------------------------------------------------------------------
class ProgramTest(unittest.TestCase):

    def test_init(self):
        program = Program()
        assert program._handle == 0
        assert program._need_update is False
        assert program._valid is False
        assert program.shaders == []

    def test_delete_no_context(self):
        program = Program()
        program.delete()

    def test_init_from_string(self):
        program = Program("A", "B")
        assert len(program.shaders) == 2
        assert program.shaders[0].code == "A"
        assert program.shaders[1].code == "B"

    def test_init_from_shader(self):
        program = Program(VertexShader("A"), FragmentShader("B"))
        assert len(program.shaders) == 2
        assert program.shaders[0].code == "A"
        assert program.shaders[1].code == "B"

    def test_unique_shader(self):
        vert = VertexShader("A")
        frag = FragmentShader("B")
        program = Program([vert, vert], [frag, frag, frag])
        assert len(program.shaders) == 2

    def test_uniform(self):
        vert = VertexShader("uniform float A;")
        frag = FragmentShader("uniform float A; uniform vec4 B;")
        program = Program(vert, frag)
        assert program.uniforms[0].name == 'A'
        assert program.uniforms[0].gtype == gl.GL_FLOAT
        assert program.uniforms[1].name == 'B'
        assert program.uniforms[1].gtype == gl.GL_FLOAT_VEC4

    def test_attributes(self):
        vert = VertexShader("attribute float A;")
        frag = FragmentShader("")
        program = Program(vert, frag)
        assert program.attributes[0].name == 'A'
        assert program.attributes[0].gtype == gl.GL_FLOAT

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

        program = Program(vert=vert)
        self.assertRaises(RuntimeError, program.activate)

        program = Program(frag=frag)
        self.assertRaises(RuntimeError, program.activate)

    def test_setitem(self):
        vert = VertexShader("")
        frag = FragmentShader("")

        program = Program(vert, frag)

        def modifier(p):
            p["A"] = 1
        self.assertRaises(NameError, modifier, program)

    def test_set_uniform_vec4(self):
        vert = VertexShader("uniform vec4 color;")
        frag = FragmentShader("")

        program = Program(vert, frag)
        program["color"] = 1, 1, 1, 1

    def test_set_attribute_float(self):

        vert = VertexShader("attribute float f;")
        frag = FragmentShader("")

        program = Program(vert, frag)
        program["f"] = VertexBuffer(np.zeros(100, dtype=np.float32))
        assert program._attributes["f"].count == 100

        program = Program(vert, frag)
        program.set_vars(f=ClientVertexBuffer(np.zeros((100, 1, 1),
                                                       dtype=np.float32)))
        assert_raises(NameError, program.set_vars, junk='foo')
        assert program._attributes["f"].count == 100

        program = Program(vert, frag)

        def modifier(p):
            p["f"] = np.zeros((100, 1, 1), dtype=np.float32)
        self.assertRaises(ValueError, modifier, program)

    def test_set_attribute_vec4(self):
        vert = VertexShader("attribute vec4 color;")
        frag = FragmentShader("")

        program = Program(vert, frag)

        def modifier(p):
            p["color"] = np.array(3, dtype=np.float32)
        self.assertRaises(ValueError, modifier, program)

        program = Program(vert, frag)

        def modifier(p):
            p["color"] = np.array((100, 5), dtype=np.float32)
        self.assertRaises(ValueError, modifier, program)

        program = Program(vert, frag)
        program["color"] = ClientVertexBuffer(
            np.zeros(
                (100, 4), dtype=np.float32))
        assert program._attributes["color"].count == 100

        program = Program(vert, frag)
        program["color"] = ClientVertexBuffer(
            np.zeros(
                (100, 1, 4), dtype=np.float32))
        assert program._attributes["color"].count == 100

        program = Program(vert, frag)
        program["color"] = ClientVertexBuffer(
            np.zeros(
                100,
                dtype=(
                    np.float32,
                    4)))
        assert program._attributes["color"].count == 100

    def test_set_vars(self):
        vert = VertexShader("attribute vec4 color;")
        frag = FragmentShader("")
        program = Program(vert, frag)
        arr = np.array((100, 5), dtype=np.float32)
        assert_raises(ValueError, program.set_vars, arr)
        dtype = np.dtype([('position', np.float32, 3),
                          ('texcoord', np.float32, 2),
                          ('color', np.float32, 4)])
        data = np.zeros(100, dtype=dtype)
        arr = VertexBuffer(data)
        program.set_vars(arr)
        assert_raises(TypeError, program.set_vars, 'hello')
        program.set_vars(dict(color=arr, fake=arr))
