# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import pytest

from vispy.util.svg.color import Color
from vispy.testing import run_tests_if_main


@pytest.mark.parametrize('content, rgba', [
    ('#ff8000', (1., 128 / 255., 0., 1.)),
    ('#FF8000', (1., 128 / 255., 0., 1.)),
    ('#f80', (1., 136 / 255., 0., 1.)),
    ('#ff800080', (1., 128 / 255., 0., 128 / 255.)),
    ('#f808', (1., 136 / 255., 0., 136 / 255.)),
    ('rgb(10, 20, 30)', (10 / 255., 20 / 255., 30 / 255., 1.)),
    ('rgb(100%, 0%, 50%)', (1., 0., 127 / 255., 1.)),
    ('rgba(10, 20, 30, 0.5)', (10 / 255., 20 / 255., 30 / 255., 0.5)),
    ('rgba(10, 20, 30, 25%)', (10 / 255., 20 / 255., 30 / 255., 0.25)),
    ('rgba(300, -5, 30, 2)', (1., 0., 30 / 255., 1.)),
    ('  red ', (1., 0., 0., 1.)),
    ('Red', (1., 0., 0., 1.)),
])
def test_color_parsing(content, rgba):
    """Test that SVG color strings are parsed, alpha included"""
    color = Color(content)
    assert color.rgba == pytest.approx(rgba)
    assert color.rgb == pytest.approx(rgba[:3])
    assert color.alpha == pytest.approx(rgba[3])


@pytest.mark.parametrize('content', [
    'notacolor', '#12', '#12345', '#gggggg', 'rgb(1, 2)', 'rgb(1, 2, 3, 4)',
    'rgba(1, 2, 3)', 'rgb(a, b, c)',
])
def test_color_invalid(content):
    """Test that unknown colors fall back to opaque black"""
    assert Color(content).rgba == (0., 0., 0., 1.)


def test_color_repr():
    """Test that the repr only carries alpha for translucent colors"""
    assert repr(Color('#ff8000')) == '#ff8000'
    assert repr(Color('rgb(10, 20, 30)')) == '#0a141e'
    assert repr(Color('#ff800080')) == '#ff800080'


run_tests_if_main()
