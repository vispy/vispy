# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import os
import re
from subprocess import CalledProcessError

from ..logs import logger
from ..wrappers import run_subprocess


def _get_dpi_from(cmd, pattern, func):
    """Match pattern against the output of func, passing the results as
    floats to func.  If anything fails, return None.
    """
    try:
        out, _ = run_subprocess([cmd])
    except (OSError, CalledProcessError):
        pass
    else:
        match = re.search(pattern, out)
        if match:
            return func(*map(float, match.groups()))


def _xrandr_calc(x_px, y_px, x_mm, y_mm):
    if x_mm == 0 or y_mm == 0:
        logger.warning("'xrandr' output has screen dimension of 0mm, " +
                       "can't compute proper DPI")
        return 96.
    return 25.4 * (x_px / x_mm + y_px / y_mm) / 2


def get_dpi(raise_error=True):
    """Get screen DPI from the OS

    Parameters
    ----------
    raise_error : bool
        If True, raise an error if DPI could not be determined.

    Returns
    -------
    dpi : float
        Dots per inch of the primary screen.
    """
    # If we are running without an X server (e.g. OSMesa), use a fixed DPI
    if 'DISPLAY' not in os.environ:
        return 96.

    from_xdpyinfo = _get_dpi_from(
        'xdpyinfo', r'(\d+)x(\d+) dots per inch',
        lambda x_dpi, y_dpi: (x_dpi + y_dpi) / 2)
    if from_xdpyinfo is not None:
        return from_xdpyinfo

    from_xrandr = _get_dpi_from(
        'xrandr', r'(\d+)x(\d+).*?(\d+)mm x (\d+)mm',
        _xrandr_calc)
    if from_xrandr is not None:
        return from_xrandr
    if raise_error:
        raise RuntimeError('could not determine DPI')
    else:
        logger.warning('could not determine DPI')
    return 96
