# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import os
import sys
import numpy as np
from nose.tools import assert_true, assert_equal
import warnings

from vispy.testing import assert_in, run_tests_if_main
from vispy.util.fonts import list_fonts, _load_glyph, _vispy_fonts

warnings.simplefilter('always')


def test_font_list():
    """Test font listing"""
    f = list_fonts()
    assert_true(len(f) > 0)
    for font in _vispy_fonts:
        assert_in(font, f)


def test_font_glyph():
    """Test loading glyphs"""
    # try both a vispy and system font
    sys_fonts = set(list_fonts()) - set(_vispy_fonts)
    assert_true(len(sys_fonts) > 0)
    for face in ('OpenSans', list(sys_fonts)[0]):
        font_dict = dict(face=face, size=12, bold=False, italic=False)
        glyphs_dict = dict()
        chars = 'foobar^C&#'
        if face != 'OpenSans' and os.getenv('APPVEYOR', '').lower() == 'true':
            continue  # strange system font failure
        if 'true' in os.getenv('TRAVIS', '') and sys.version[0] == '3':
            continue  # as of April 2015 strange FontConfig error on Travis
        for char in chars:
            # Warning that Arial might not exist
            _load_glyph(font_dict, char, glyphs_dict)
        assert_equal(len(glyphs_dict), np.unique([c for c in chars]).size)


run_tests_if_main()
