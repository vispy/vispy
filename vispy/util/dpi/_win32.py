# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ...ext.gdi32plus import (gdi32, user32, HORZSIZE, VERTSIZE,
                              HORZRES, VERTRES)


def get_dpi():
    """Get screen DPI from the OS"""
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    h_size = gdi32.GetDeviceCaps(dc, HORZSIZE)
    v_size = gdi32.GetDeviceCaps(dc, VERTSIZE)
    h_res = gdi32.GetDeviceCaps(dc, HORZRES)
    v_res = gdi32.GetDeviceCaps(dc, VERTRES)
    user32.ReleaseDC(None, dc)
    return (h_res/float(h_size) + v_res/float(v_size)) * 0.5 * 25.4
