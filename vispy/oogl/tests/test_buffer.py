# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
import OpenGL.GL as gl

from vispy.oogl.buffer import Buffer
from vispy.oogl.buffer import VertexBuffer
from vispy.oogl.buffer import VertexBufferView
from vispy.oogl.buffer import IndexBuffer



# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    def test_init(self):
        buffer = Buffer()
        assert buffer._handle == 0
        assert buffer.dirty   == True
        assert buffer.status  == False
        assert buffer.data    == None
        assert buffer.size    == 0
        assert buffer.stride  == 0
        assert buffer.offset  == 0
        assert buffer.gtype   == 0

    def test_size_gtype(self):

        data = np.zeros(100, np.float32)
        buffer = Buffer(data)
        assert buffer.size == 100
        assert buffer.gtype == gl.GL_FLOAT

        data = np.zeros((100,4), np.float32)
        buffer = Buffer(data)
        assert buffer.size == 100
        assert buffer.gtype == gl.GL_FLOAT_VEC4

        data = np.zeros((100,4,4), np.float32)
        buffer = Buffer(data)
        assert buffer.size == 100
        assert buffer.gtype == gl.GL_FLOAT_MAT4

        data = np.zeros((100,4,4), np.float32)
        buffer = Buffer(data)
        assert buffer.size == 100
        assert buffer.gtype == gl.GL_FLOAT_MAT4

        data = np.zeros(100, [('a', np.float32, (4,4))])
        buffer = Buffer(data['a'])
        assert buffer.size == 100
        assert buffer.gtype == gl.GL_FLOAT_MAT4


if __name__ == "__main__":
    unittest.main()
