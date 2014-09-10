# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ._testing import (SkipTest, requires_application, requires_img_lib,  # noqa
                      assert_is, assert_in, assert_not_in, has_backend,  # noqa
                      glut_skip, requires_pyopengl, requires_scipy,  # noqa
                      has_matplotlib, assert_image_equal,  # noqa
                      save_testing_image, TestingCanvas, has_pyopengl,  # noqa
                      run_tests_if_main)  # noqa
from ._runners import _tester  # noqa
