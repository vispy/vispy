# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# Force the selection of an application backend. If the user has already
# imported PyQt or PySide, this should result in selection of the corresponding
# backend.
from .backends import qt_lib

if qt_lib is None:
    raise RuntimeError("Module backends._qt should not be imported directly.")
elif qt_lib in 'pyqt4':
    from PyQt4 import QtGui
    QWidget, QGridLayout = QtGui.QWidget, QtGui.QGridLayout  # Compat
elif qt_lib == 'pyside':
    from PySide import QtGui
    QWidget, QGridLayout = QtGui.QWidget, QtGui.QGridLayout  # Compat
elif qt_lib == 'pyqt5':
    from PyQt5 import QtWidgets
    QWidget, QGridLayout = QtWidgets.QWidget, QtWidgets.QGridLayout  # Compat
elif qt_lib == 'pyqt6':
    from PyQt6 import QtWidgets
    QWidget, QGridLayout = QtWidgets.QWidget, QtWidgets.QGridLayout  # Compat
elif qt_lib == 'pyside2':
    from PySide2 import QtWidgets
    QWidget, QGridLayout = QtWidgets.QWidget, QtWidgets.QGridLayout  # Compat
elif qt_lib == 'pyside6':
    from PySide6 import QtWidgets
    QWidget, QGridLayout = QtWidgets.QWidget, QtWidgets.QGridLayout  # Compat
elif qt_lib:
    raise RuntimeError("Invalid value for qt_lib %r." % qt_lib)
else:
    raise RuntimeError("Module backends._qt should not be imported directly.")


class QtCanvas(QWidget):
    """Qt widget containing a vispy Canvas.

    This is a convenience class that allows a vispy canvas to be embedded
    directly into a Qt application.
    All methods and properties of the Canvas are wrapped by this class.

    Parameters
    ----------
    parent : QWidget or None
        The Qt parent to assign to this widget.
    canvas : instance or subclass of Canvas
        The vispy Canvas to display inside this widget, or a Canvas subclass
        to instantiate using any remaining keyword arguments.
    """

    def __init__(self, parent=None, canvas=None, **kwargs):
        from .canvas import Canvas
        if canvas is None:
            canvas = Canvas
        if issubclass(canvas, Canvas):
            canvas = canvas(**kwargs)
        elif len(**kwargs) > 0:
            raise TypeError('Invalid keyword arguments: %s' %
                            list(kwargs.keys()))
        if not isinstance(canvas, Canvas):
            raise TypeError('canvas argument must be an instance or subclass '
                            'of Canvas.')

        QWidget.__init__(self, parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self._canvas = canvas
        self.layout.addWidget(canvas.native)
        self.setSizePolicy(canvas.native.sizePolicy())

    def __getattr__(self, attr):
        if hasattr(self._canvas, attr):
            return getattr(self._canvas, attr)
        else:
            raise AttributeError(attr)

    def update(self):
        """Call update() on both this widget and the internal canvas."""
        QWidget.update(self)
        self._canvas.update()


class QtSceneCanvas(QtCanvas):
    """Convenience class embedding a vispy SceneCanvas inside a QWidget.
    See QtCanvas.
    """

    def __init__(self, parent=None, **kwargs):
        from ..scene.canvas import SceneCanvas
        QtCanvas.__init__(self, parent, canvas=SceneCanvas, **kwargs)
