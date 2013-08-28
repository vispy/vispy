# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from vispy import gl

from vispy.oogl.buffer import Buffer
from vispy.oogl.buffer import VertexBuffer
from vispy.oogl.buffer import VertexBufferView
from vispy.oogl.buffer import ElementBuffer



# -----------------------------------------------------------------------------
class BufferTest(unittest.TestCase):

    def test_init(self):
        buffer = Buffer(gl.GL_ARRAY_BUFFER)
        assert buffer._handle      == 0
        assert buffer._need_update == False
        assert buffer._valid       == False
        assert buffer._size        == 0



if __name__ == "__main__":
    unittest.main()
