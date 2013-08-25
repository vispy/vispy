# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
import OpenGL.GL as gl
from vispy.oogl.shader import VertexShader, FragmentShader


class VertexShaderTest(unittest.TestCase):

    def test_init(self):
        shader = VertexShader()

        assert shader._target      == gl.GL_VERTEX_SHADER
        assert shader._handle      == 0
        assert shader._valid       == False
        assert shader._need_update == False
        assert shader._id          == 1



class FragmentShaderTest(unittest.TestCase):

    def test_init(self):
        shader = FragmentShader()

        assert shader._target      == gl.GL_FRAGMENT_SHADER
        assert shader._handle      == 0
        assert shader._valid       == False
        assert shader._need_update == False
        assert shader._id          == 1


if __name__ == "__main__":
    unittest.main()
