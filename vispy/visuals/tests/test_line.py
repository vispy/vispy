# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
import pytest

from vispy.visuals.line import LineVisual, ArrowVisual
from vispy.visuals.line.line import _AggLineVisual
from vispy.scene import visuals


def test_line_visual_agg_dimension_check():
    """Test that agg line method rejects 3D coordinates."""
    pos_2d = np.array([[0, 0], [1, 1]], dtype=np.float32)
    pos_3d = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)

    # 2D works with agg
    line2d = LineVisual(pos=pos_2d, method='agg')
    assert line2d.method == 'agg'

    # 3D works with gl
    line3d = LineVisual(pos=pos_3d, method='gl')
    assert line3d.method == 'gl'

    # 3D with agg on init raises ValueError
    with pytest.raises(ValueError, match="Line method 'agg' only supports 2D coordinates"):
        LineVisual(pos=pos_3d, method='agg')

    # Setting pos to 3D when method is agg raises ValueError
    with pytest.raises(ValueError, match="Line method 'agg' only supports 2D coordinates"):
        line2d.set_data(pos=pos_3d)

    # Switching method to agg when pos is 3D raises ValueError
    with pytest.raises(ValueError, match="Line method 'agg' only supports 2D coordinates"):
        line3d.method = 'agg'


def test_arrow_visual_agg_dimension_check():
    """Test that agg arrow method rejects 3D coordinates and arrows."""
    line_3d = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
    arrows_3d = line_3d.reshape(1, 6)

    line_2d = np.array([[0, 0], [1, 1]], dtype=np.float32)
    arrows_2d = line_2d.reshape(1, 4)

    # 2D arrows work with agg
    arrow2d = ArrowVisual(pos=line_2d, arrows=arrows_2d, method='agg')
    assert arrow2d.method == 'agg'

    # 3D arrows work with gl
    arrow3d = ArrowVisual(pos=line_3d, arrows=arrows_3d, method='gl')
    assert arrow3d.method == 'gl'

    # 3D arrows on init with agg raises ValueError
    with pytest.raises(ValueError, match="Line method 'agg' only supports 2D coordinates"):
        ArrowVisual(pos=line_3d, arrows=arrows_3d, method='agg')

    # 3D arrows only (no pos) with agg raises ValueError
    with pytest.raises(ValueError, match="Arrow method 'agg' only supports 2D arrows"):
        ArrowVisual(arrows=arrows_3d, method='agg')

    # Switching method to agg on 3D arrows raises ValueError
    with pytest.raises(ValueError):
        arrow3d.method = 'agg'


def test_agg_bake_dimension_check():
    """Test that _AggLineVisual._agg_bake rejects 3D vertices."""
    vertices_3d = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
    with pytest.raises(ValueError, match="Line method 'agg' only supports 2D coordinates"):
        _AggLineVisual._agg_bake(vertices_3d, color=np.array([1, 1, 1, 1]))
