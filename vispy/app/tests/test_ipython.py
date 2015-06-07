# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Tests for Vispy's ipython bindings"""

# from vispy import ipython
from numpy.testing import assert_equal
from IPython.testing.globalipapp import get_ipython


def test_webgl_loading():
    """Test if the vispy.ipython extension loads
        the webGL backend"""
    ipy = get_ipython()
    ipy.run_cell("from vispy import app")
    ipy.run_cell("%load_ext vispy.ipython")
    ipy.run_cell("backend_name = app.use_app().backend_name")

    # make sure that the webgl backend got loaded
    assert_equal(ipy.user_ns["backend_name"], "ipynb_webgl")
