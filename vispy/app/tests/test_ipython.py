# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Tests for Vispy's IPython bindings"""

# from vispy import IPython
from numpy.testing import assert_equal
from vispy.testing import requires_ipython


@requires_ipython(2.0)
def test_webgl_loading():
    """Test if the vispy.ipython extension loads the webGL backend
    on IPython 3.0 and greater.

    Test if it fails to load the webGL backend for IPython versions
    less that 3.0"""

    import IPython
    from distutils.version import LooseVersion
    from IPython.testing.globalipapp import get_ipython

    ipy = get_ipython()
    ipy.run_cell("from vispy import app")

    if LooseVersion(IPython.__version__) >= LooseVersion("3.0.0"):
        ipy.run_cell("%load_ext vispy.ipython")
        ipy.run_cell("backend_name = app.use_app().backend_name")
        # make sure that the webgl backend got loaded
        assert_equal(ipy.user_ns["backend_name"], "ipynb_webgl")
    else:
        ipy.run_cell("%load_ext vispy.ipython")
        # HACK: duplicate code branches for now to see what happens. 
        ipy.run_cell("backend_name = app.use_app().backend_name")
        # make sure that the webgl backend got loaded
        assert_equal(ipy.user_ns["backend_name"], "ipynb_webgl")