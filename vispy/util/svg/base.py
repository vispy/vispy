# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

namespace = '{http://www.w3.org/2000/svg}'
dpi = 90
units = {
    None: 1,           # Default unit (same as pixel)
    'px': 1,           # px: pixel. Default SVG unit
    'em': 10,          # 1 em = 10 px FIXME
    'ex': 5,           # 1 ex =  5 px FIXME
    'in': dpi,          # 1 in = 96 px
    'cm': dpi / 2.54,   # 1 cm = 1/2.54 in
    'mm': dpi / 25.4,   # 1 mm = 1/25.4 in
    'pt': dpi / 72.0,   # 1 pt = 1/72 in
    'pc': dpi / 6.0,    # 1 pc = 1/6 in
    '%': 1 / 100.0   # 1 percent
}
