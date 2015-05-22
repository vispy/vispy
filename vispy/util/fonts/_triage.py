# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import sys

from ._vispy_fonts import _vispy_fonts
if sys.platform.startswith('linux'):
    from ._freetype import _load_glyph
    from ...ext.fontconfig import _list_fonts
elif sys.platform == 'darwin':
    from ._quartz import _load_glyph, _list_fonts
elif sys.platform.startswith('win'):
    from ._freetype import _load_glyph  # noqa, analysis:ignore
    from ._win32 import _list_fonts  # noqa, analysis:ignore
else:
    raise NotImplementedError('unknown system %s' % sys.platform)

_fonts = {}


def list_fonts():
    """List system fonts

    Returns
    -------
    fonts : list of str
        List of system fonts.
    """
    vals = _list_fonts()
    for font in _vispy_fonts:
        vals += [font] if font not in vals else []
    vals = sorted(vals, key=lambda s: s.lower())
    return vals
