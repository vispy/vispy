import numpy as np
from nose.tools import assert_true, assert_equal
import warnings

from vispy.testing import assert_in
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
    for face in ('OpenSans', list_fonts()[0]):
        font_dict = dict(face=face, size=12, bold=False, italic=False)
        glyphs_dict = dict()
        chars = 'foobar^C&#'
        for char in chars:
            # Warning that Arial might not exist
            _load_glyph(font_dict, char, glyphs_dict)
        assert_equal(len(glyphs_dict), np.unique([c for c in chars]).size)
