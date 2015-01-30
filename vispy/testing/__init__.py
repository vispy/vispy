# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ._testing import (SkipTest, requires_application, requires_img_lib,  # noqa
                      has_backend, requires_pyopengl,  # noqa
                      requires_scipy, has_matplotlib,  # noqa
                      save_testing_image, TestingCanvas, has_pyopengl,  # noqa
                      run_tests_if_main, assert_image_equal,
                      assert_is, assert_in, assert_not_in, assert_equal,
                      assert_not_equal, assert_raises, assert_true)  # noqa
from ._runners import test  # noqa
