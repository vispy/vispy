# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Functional regression tests for Qt mouse button mapping (#2751)."""

from vispy.app import Canvas, use_app
from vispy.testing import run_tests_if_main, requires_application


def _qt_modules():
    """Return (QtCore, QtGui, backend_module) after loading PyQt6."""
    use_app('pyqt6')
    from PyQt6 import QtCore, QtGui
    import sys
    qt_backend = sys.modules['vispy.app.backends._qt']
    return QtCore, QtGui, qt_backend


def _make_mouse_event(QtCore, QtGui, event_type, button, buttons=None):
    """Build a real Qt mouse event for the given button."""
    if buttons is None:
        buttons = QtCore.Qt.MouseButton.NoButton
    pos = QtCore.QPointF(12.0, 34.0)
    return QtGui.QMouseEvent(
        event_type,
        pos,
        pos,  # global position
        button,
        buttons,
        QtCore.Qt.KeyboardModifier.NoModifier,
    )


class _UnknownButtonEvent:
    """Minimal stand-in for a Qt mouse event with an unmapped button value."""

    def __init__(self, button_value, QtCore):
        self._button_value = button_value
        self._QtCore = QtCore
        self.ignored = False

    def button(self):
        return self._button_value

    def buttons(self):
        return self._QtCore.Qt.MouseButton.NoButton

    def pos(self):
        # Used by _get_event_xy on some Qt bindings.
        class _P:
            def x(self):
                return 1

            def y(self):
                return 2

        return _P()

    def position(self):
        return self.pos()

    def modifiers(self):
        return self._QtCore.Qt.KeyboardModifier.NoModifier

    def ignore(self):
        self.ignored = True


@requires_application('pyqt6')
def test_standard_and_extra_button_release_events():
    """Release of standard and Extra buttons must emit the mapped VisPy id."""
    QtCore, QtGui, qt_backend = _qt_modules()
    mb = QtCore.Qt.MouseButton
    buttonmap = qt_backend.BUTTONMAP

    cases = [
        (mb.LeftButton, 1),
        (mb.RightButton, 2),
        (mb.MiddleButton, 3),
        (mb.BackButton, 4),
        (mb.ForwardButton, 5),
        (mb.ExtraButton3, 6),   # TaskButton
        (mb.ExtraButton4, 7),
        (mb.ExtraButton24, 27),
    ]
    # Sanity: mapping table matches expectations.
    for qt_button, vispy_button in cases:
        assert buttonmap[qt_button] == vispy_button

    app = use_app('pyqt6')
    canvas = Canvas(app=app, size=(80, 80), show=False, create_native=True)
    try:
        backend = canvas._backend
        for qt_button, vispy_button in cases:
            seen = []
            canvas.events.mouse_release.connect(lambda e, s=seen: s.append(e))
            ev = _make_mouse_event(
                QtCore, QtGui, QtCore.QEvent.Type.MouseButtonRelease, qt_button
            )
            backend.mouseReleaseEvent(ev)
            assert len(seen) == 1, (qt_button, vispy_button)
            assert seen[0].button == vispy_button
            assert tuple(seen[0].pos) == (12.0, 34.0)
            canvas.events.mouse_release.disconnect()
    finally:
        canvas.close()


@requires_application('pyqt6')
def test_unmapped_button_release_does_not_raise():
    """#2751: unknown Qt button on release must not KeyError; VisPy gets 0."""
    QtCore, QtGui, qt_backend = _qt_modules()
    app = use_app('pyqt6')
    canvas = Canvas(app=app, size=(80, 80), show=False, create_native=True)
    try:
        seen = []
        canvas.events.mouse_release.connect(lambda e: seen.append(e))
        # Choose a value that is not a MouseButton flag in BUTTONMAP.
        unknown = object()
        assert unknown not in qt_backend.BUTTONMAP
        fake = _UnknownButtonEvent(unknown, QtCore)
        # Must not raise KeyError (the original bug).
        canvas._backend.mouseReleaseEvent(fake)
        assert len(seen) == 1
        assert seen[0].button == 0
    finally:
        canvas.close()


@requires_application('pyqt6')
def test_press_and_double_click_extra_buttons():
    """Press / double-click must use the same mapping as release."""
    QtCore, QtGui, qt_backend = _qt_modules()
    mb = QtCore.Qt.MouseButton
    app = use_app('pyqt6')
    canvas = Canvas(app=app, size=(80, 80), show=False, create_native=True)
    try:
        backend = canvas._backend

        press_seen = []
        canvas.events.mouse_press.connect(lambda e: press_seen.append(e))
        press_ev = _make_mouse_event(
            QtCore, QtGui, QtCore.QEvent.Type.MouseButtonPress, mb.ExtraButton4,
            buttons=mb.ExtraButton4,
        )
        backend.mousePressEvent(press_ev)
        assert len(press_seen) == 1
        assert press_seen[0].button == 7
        assert 7 in press_seen[0].buttons

        dbl_seen = []
        canvas.events.mouse_double_click.connect(lambda e: dbl_seen.append(e))
        dbl_ev = _make_mouse_event(
            QtCore, QtGui,
            QtCore.QEvent.Type.MouseButtonDblClick,
            mb.ExtraButton3,
        )
        backend.mouseDoubleClickEvent(dbl_ev)
        assert len(dbl_seen) == 1
        assert dbl_seen[0].button == 6
    finally:
        canvas.close()


@requires_application('pyqt6')
def test_buttonmap_to_list_includes_extra_buttons():
    """Multi-button state must report Extra buttons, not only 1-5."""
    QtCore, QtGui, qt_backend = _qt_modules()
    mb = QtCore.Qt.MouseButton
    helper = qt_backend.QtBaseCanvasBackend._buttonmap_to_list

    class _Dummy:
        pass

    mixed = mb.LeftButton | mb.ForwardButton | mb.ExtraButton4
    assert helper(_Dummy(), mixed) == [1, 5, 7]


run_tests_if_main()
