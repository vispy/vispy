# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Functional regression tests for Qt mouse button mapping (#2751)."""

import pytest

from vispy.app import Canvas, use_app
from vispy.testing import run_tests_if_main, requires_application


def _make_mouse_event(event_type_name, button, buttons=None):
    """Build a real Qt mouse event for the given button."""
    from PyQt6 import QtCore, QtGui

    if buttons is None:
        buttons = QtCore.Qt.MouseButton.NoButton
    pos = QtCore.QPointF(12.0, 34.0)
    return QtGui.QMouseEvent(
        getattr(QtCore.QEvent.Type, event_type_name),
        pos,
        pos,  # global position
        button,
        buttons,
        QtCore.Qt.KeyboardModifier.NoModifier,
    )


class _UnknownButtonEvent:
    """Minimal stand-in for a Qt mouse event with an unmapped button value."""

    def __init__(self, button_value):
        self._button_value = button_value
        self.ignored = False

    def button(self):
        return self._button_value

    def buttons(self):
        from PyQt6 import QtCore

        return QtCore.Qt.MouseButton.NoButton

    def pos(self):
        class _P:
            def x(self):
                return 1

            def y(self):
                return 2

        return _P()

    def position(self):
        return self.pos()

    def modifiers(self):
        from PyQt6 import QtCore

        return QtCore.Qt.KeyboardModifier.NoModifier

    def ignore(self):
        self.ignored = True


# (event_name, qt_event_type, qt_button, expected_vispy_button, buttons_flag)
_EVENT_CASES = [
    ('release', 'MouseButtonRelease', 'LeftButton', 1, None),
    ('release', 'MouseButtonRelease', 'RightButton', 2, None),
    ('release', 'MouseButtonRelease', 'MiddleButton', 3, None),
    ('release', 'MouseButtonRelease', 'BackButton', 4, None),
    ('release', 'MouseButtonRelease', 'ForwardButton', 5, None),
    ('release', 'MouseButtonRelease', 'ExtraButton3', 6, None),
    ('release', 'MouseButtonRelease', 'ExtraButton4', 7, None),
    ('release', 'MouseButtonRelease', 'ExtraButton24', 27, None),
    ('press', 'MouseButtonPress', 'ExtraButton4', 7, 'ExtraButton4'),
    ('double_click', 'MouseButtonDblClick', 'ExtraButton3', 6, None),
]

_HANDLER = {
    'press': 'mousePressEvent',
    'release': 'mouseReleaseEvent',
    'double_click': 'mouseDoubleClickEvent',
}

_VISPY_EVENT = {
    'press': 'mouse_press',
    'release': 'mouse_release',
    'double_click': 'mouse_double_click',
}


@requires_application('pyqt6')
@pytest.mark.parametrize(
    'event_name, event_type, qt_button, vispy_button, buttons_flag',
    _EVENT_CASES,
    ids=[
        f'{name}-{vispy}'
        for name, _, _, vispy, _ in _EVENT_CASES
    ],
)
def test_mapped_button_events(event_name, event_type, qt_button, vispy_button,
                              buttons_flag):
    """Press / release / double-click must emit the mapped VisPy button id."""
    app = use_app('pyqt6')
    from PyQt6 import QtCore
    from vispy.app.backends import _qt as qt_backend

    qt_button = getattr(QtCore.Qt.MouseButton, qt_button)
    if buttons_flag is not None:
        buttons_flag = getattr(QtCore.Qt.MouseButton, buttons_flag)
    assert qt_backend.BUTTONMAP[qt_button] == vispy_button

    with Canvas(app=app, size=(80, 80), create_native=True) as canvas:
        seen = []
        canvas.events[_VISPY_EVENT[event_name]].connect(lambda e: seen.append(e))
        ev = _make_mouse_event(event_type, qt_button, buttons=buttons_flag)
        getattr(canvas._backend, _HANDLER[event_name])(ev)
        assert len(seen) == 1
        assert seen[0].button == vispy_button
        if event_name == 'release':
            assert tuple(seen[0].pos) == (12.0, 34.0)
        if buttons_flag is not None:
            assert vispy_button in seen[0].buttons


@requires_application('pyqt6')
def test_unmapped_button_release_does_not_raise():
    """#2751: unknown Qt button on release must not KeyError; VisPy gets 0."""
    app = use_app('pyqt6')
    from vispy.app.backends import _qt as qt_backend

    with Canvas(app=app, size=(80, 80), create_native=True) as canvas:
        seen = []
        canvas.events.mouse_release.connect(lambda e: seen.append(e))
        unknown = object()
        assert unknown not in qt_backend.BUTTONMAP
        fake = _UnknownButtonEvent(unknown)
        # Must not raise KeyError (the original bug in GH #2751).
        canvas._backend.mouseReleaseEvent(fake)
        assert len(seen) == 1
        assert seen[0].button == 0


@requires_application('pyqt6')
def test_buttonmap_to_list_includes_extra_buttons():
    """Multi-button state must report Extra buttons, not only 1-5."""
    use_app('pyqt6')
    from PyQt6 import QtCore
    from vispy.app.backends import _qt as qt_backend

    mb = QtCore.Qt.MouseButton
    mixed = mb.LeftButton | mb.ForwardButton | mb.ExtraButton4
    assert qt_backend._buttonmap_to_list(mixed) == [1, 5, 7]


run_tests_if_main()
