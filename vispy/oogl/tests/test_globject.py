# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Vispy - Copyright (c) 2013, Vispy Development Team. All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
from vispy import gl

from vispy.oogl.globject import GLObject




class GLObjectTest(unittest.TestCase):

    def test_init(self):
        obj = GLObject()
        assert obj._handle  == 0
        assert obj._need_update == False
        assert obj._valid  == False
        # assert obj._id   == 1


if __name__ == "__main__":
    unittest.main()
