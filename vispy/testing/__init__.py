# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Testing
=======
This module provides functions useful for running tests in vispy.

Tests can be run in a few ways:

    * From Python, you can import ``vispy`` and do ``vispy.test()``.
    * From the source root, you can do ``make test`` which wraps to
      a call to ``python make test``.

There are various different testing "modes", including:

    * "full": run all tests.
    * any backend name (e.g., "glfw"): run application/GL tests using a
      specific backend.
    * "nobackend": run tests that do not require a backend.
    * "examples": run repo examples to check for errors and warnings.
    * "flake": check style errors.

Examples get automatically tested unless they have a special comment toward
the top ``# vispy: testskip``. Examples that should be tested should be
formatted so that 1) a ``Canvas`` class is defined, or a ``canvas`` class
is instantiated; and 2) the ``app.run()`` call is protected by a check
if ``__name__ == "__main__"``. This makes it so that the event loop is not
started when running examples in the test suite -- the test suite instead
manually updates the canvas (using ``app.process_events()``) for under one
second to ensure that things like timer events are processed.

For examples on how to test various bits of functionality (e.g., application
functionality, or drawing things with OpenGL), it's best to look at existing
examples in the test suite.

The code base gets automatically tested by GitHub Actions. There are multiple
testing modes that use e.g. full dependencies, minimal dependencies, etc.
See ``.github/workflows/main.yml`` to determine what automatic tests are run.
"""

from ._testing import (
    SkipTest,
    requires_application,
    requires_ipython,
    requires_img_lib,
    requires_pyopengl,
    requires_scipy,
    save_testing_image,
    TestingCanvas,
    has_pyopengl,
    run_tests_if_main,
    requires_ssl,
    assert_is,
    assert_in,
    assert_not_in,
    assert_equal,
    assert_not_equal,
    assert_raises,
    assert_true,
    raises,
    requires_numpydoc,
    IS_TRAVIS_CI,
    IS_CI,
)
from ._runners import test


__all__ = (
    "SkipTest",
    "requires_application",
    "requires_ipython",
    "requires_img_lib",
    "requires_pyopengl",
    "requires_scipy",
    "save_testing_image",
    "TestingCanvas",
    "has_pyopengl",
    "run_tests_if_main",
    "requires_ssl",
    "assert_is",
    "assert_in",
    "assert_not_in",
    "assert_equal",
    "assert_not_equal",
    "assert_raises",
    "assert_true",
    "raises",
    "requires_numpydoc",
    "IS_TRAVIS_CI",
    "IS_CI",
    "test",
)
