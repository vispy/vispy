# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ...ext.gdi32plus import (gdi32, user32, HORZSIZE, VERTSIZE,
                              HORZRES, VERTRES)


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
    try:
        user32.SetProcessDPIAware()
    except AttributeError:
        pass  # not present on XP
    dc = user32.GetDC(0)
    h_size = gdi32.GetDeviceCaps(dc, HORZSIZE)
    v_size = gdi32.GetDeviceCaps(dc, VERTSIZE)
    h_res = gdi32.GetDeviceCaps(dc, HORZRES)
    v_res = gdi32.GetDeviceCaps(dc, VERTRES)
    user32.ReleaseDC(None, dc)
    return (h_res/float(h_size) + v_res/float(v_size)) * 0.5 * 25.4
