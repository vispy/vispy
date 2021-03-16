# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
import warnings

from vispy.testing import assert_in, run_tests_if_main
from vispy.util.fonts import list_fonts, _load_glyph, _vispy_fonts
import pytest

known_bad_fonts = set([
    'Noto Color Emoji',  # https://github.com/vispy/vispy/issues/1771
    'Bahnschrift',  # https://github.com/vispy/vispy/pull/1974
])

# try both a vispy and system font   <--- what does this mean???
sys_fonts = set(list_fonts()) - set(_vispy_fonts)


def test_font_list():
    """Test font listing"""
    f = list_fonts()
    assert len(f) > 0
    for font in _vispy_fonts:
        assert_in(font, f)


@pytest.mark.parametrize('face', ['OpenSans'] + sorted(sys_fonts))
def test_font_glyph(face):
    """Test loading glyphs"""
    if face in known_bad_fonts or face.split(" ")[0] in known_bad_fonts:
        pytest.xfail()
    font_dict = dict(face=face, size=12, bold=False, italic=False)
    glyphs_dict = dict()
    chars = 'foobar^C&#'
    for char in chars:
        # Warning that Arial might not exist
        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')
            _load_glyph(font_dict, char, glyphs_dict)
    assert len(glyphs_dict) == np.unique([c for c in chars]).size


run_tests_if_main()
