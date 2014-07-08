# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import unittest
from vispy.gloo.globject import GLObject


# -----------------------------------------------------------------------------
class GLObjectTest(unittest.TestCase):

    # Default init
    # ------------
    def test_init_default(self):
        O = GLObject()

        assert O._handle == -1
        assert O._target is None
        assert O._need_create is True
        assert O._need_delete is False
        assert O._id > 0
        assert O._id == GLObject._idcount
if __name__ == "__main__":
    unittest.main()
