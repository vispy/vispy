# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Regression tests for Qt mouse button mapping (#2751)."""

from pathlib import Path

from vispy.testing import run_tests_if_main


def _qt_backend_source() -> str:
    try:
        from vispy.app.backends import _qt as qt_backend
        return Path(qt_backend.__file__).read_text(encoding='utf-8')
    except Exception:
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


run_tests_if_main()
