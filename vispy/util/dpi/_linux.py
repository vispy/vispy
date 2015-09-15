# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
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
        lambda x_px, y_px, x_mm, y_mm: 25.4 * (x_px / x_mm + y_px / y_mm) / 2)
    if from_xrandr is not None:
        return from_xrandr
    if raise_error:
        raise RuntimeError('could not determine DPI')
    else:
        logger.warning('could not determine DPI')
    return 96
