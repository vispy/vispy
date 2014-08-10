# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


# Define test proxy function, so we don't have to import vispy.testing always
def test(label='full', coverage=False, verbosity=1, *extra_args):
    """Test vispy software

    Parameters
    ----------
    label : str
        Can be one of 'full', 'nose', 'nobackend', 'extra', 'lineendings',
        'flake', or any backend name (e.g., 'qt').
    coverage : bool
        Produce coverage outputs (.coverage file and printing).
    verbosity : int
        Verbosity level to use when running ``nose``.
    """
    from ..testing import _tester
    return _tester(label, coverage, verbosity, extra_args)
