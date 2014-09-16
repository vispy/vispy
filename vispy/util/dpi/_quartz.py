# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ...ext.cocoapy import quartz


def get_dpi():
    """Get screen DPI from the OS"""
    display = quartz.CGMainDisplayID()
    mm = quartz.CGDisplayScreenSize(display)
    px = quartz.CGDisplayBounds(display).size
    return (px.width/mm.width + px.height/mm.height) * 0.5 * 25.4
