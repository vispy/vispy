# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import vispy.plot as vp
from vispy.testing import (assert_raises, requires_application,
                           run_tests_if_main)


@requires_application()
def test_figure_creation():
    """Test creating a figure"""
    with vp.Fig(show=False) as fig:
        fig[0, 0:2]
        fig[1:3, 0:2]
        ax_right = fig[1:3, 2]
        assert fig[1:3, 2] is ax_right
        # collision
        assert_raises(ValueError, fig.__getitem__, (slice(1, 3), 1))

run_tests_if_main()
