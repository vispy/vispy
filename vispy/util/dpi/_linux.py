# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..wrappers import run_subprocess


def get_dpi():
    """Get screen DPI from the OS"""
    out = run_subprocess(['xdpyinfo'])[0]
    for line in out.splitlines(False):
        if 'dots per inch' in line:
            # "    resolution:    96x96 dots per inch"
            dpi = line.strip().split()[1].split('x')
            assert len(dpi) == 2, dpi
            break
    else:
        raise RuntimeError('could not determine DPI')
    dpi = sum([float(x) for x in dpi]) / 2.
    return dpi
