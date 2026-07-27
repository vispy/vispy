# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Regression tests for Qt mouse button mapping (#2751)."""

import sys
from pathlib import Path

from vispy.testing import run_tests_if_main, requires_application


def _qt_backend_source() -> str:
    try:
        from vispy.app import use_app
        use_app('pyqt6')  # ensure _qt is loaded when available
    except Exception:
        pass
    qt_mod = sys.modules.get('vispy.app.backends._qt')
    if qt_mod is not None:
        return Path(qt_mod.__file__).read_text(encoding='utf-8')
    here = Path(__file__).resolve()
    qt_path = here.parents[1] / 'backends' / '_qt.py'
    return qt_path.read_text(encoding='utf-8')


def _method_body(src: str, method_name: str) -> str:
    token = f'def {method_name}'
    start = src.index(token)
    next_def = src.find('\n    def ', start + len(token))
    if next_def == -1:
        return src[start:]
    return src[start:next_def]


def _load_qt_backend():
    from vispy.app import use_app
    use_app('pyqt6')
    qt_mod = sys.modules.get('vispy.app.backends._qt')
    if qt_mod is None:
        raise RuntimeError('Qt backend module was not loaded')
    return qt_mod


def test_mouse_release_uses_buttonmap_get():
    """Extra mouse buttons must not KeyError on release (#2751)."""
    src = _qt_backend_source()
    body = _method_body(src, 'mouseReleaseEvent')
    assert 'BUTTONMAP.get(' in body
    assert 'BUTTONMAP[ev.button()]' not in body


def test_mouse_press_and_double_click_keep_get():
    src = _qt_backend_source()
    assert 'BUTTONMAP.get(' in _method_body(src, 'mousePressEvent')
    assert 'BUTTONMAP.get(' in _method_body(src, 'mouseDoubleClickEvent')


def test_buttonmap_get_fallback_semantics():
    sample = {1: 1, 2: 2, 4: 3}
    assert sample.get(8, 0) == 0
    assert sample.get(1, 0) == 1


@requires_application('pyqt6')
def test_buttonmap_includes_qt_extra_buttons():
    """Qt ExtraButton3..24 should map to distinct VisPy ids 6..27."""
    from PyQt6.QtCore import Qt

    qt_backend = _load_qt_backend()
    buttonmap = qt_backend.BUTTONMAP
    mb = Qt.MouseButton

    # Standard buttons keep historical VisPy ids.
    assert buttonmap[mb.NoButton] == 0
    assert buttonmap[mb.LeftButton] == 1
    assert buttonmap[mb.RightButton] == 2
    assert buttonmap[mb.MiddleButton] == 3
    assert buttonmap[mb.BackButton] == 4
    assert buttonmap[mb.ForwardButton] == 5

    # ExtraButton1/2 are aliases of Back/Forward (already 4/5).
    assert mb.ExtraButton1 == mb.BackButton
    assert mb.ExtraButton2 == mb.ForwardButton

    # ExtraButton3..24 become VisPy 6..27 so callers can bind them.
    for extra_i in range(3, 25):
        qt_button = getattr(mb, f'ExtraButton{extra_i}')
        assert buttonmap[qt_button] == extra_i + 3


@requires_application('pyqt6')
def test_buttonmap_to_list_reports_extra_buttons():
    from PyQt6.QtCore import Qt

    qt_backend = _load_qt_backend()
    helper = qt_backend.QtBaseCanvasBackend._buttonmap_to_list

    class _Dummy:
        pass

    mb = Qt.MouseButton
    mixed = mb.LeftButton | mb.ExtraButton4 | mb.ForwardButton
    got = helper(_Dummy(), mixed)
    # Left=1, Forward=5, ExtraButton4 -> VisPy 7
    assert got == [1, 5, 7]


run_tests_if_main()
