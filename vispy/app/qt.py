# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# Force the selection of an application backend. If the user has already
# imported PyQt or PySide, this should result in selection of the corresponding
# backend.
from . import use_app
app = use_app()
try:
    QtGui = app.backend_module.QtGui
except AttributeError:
    raise RuntimeError("Cannot import Qt library; non-Qt backend is already "
                       "in use.")


class QtCanvas(QtGui.QWidget):
    """ Qt widget containing a vispy Canvas. 
    
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
            
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout()
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
        """Call update() on both this widget and the internal canvas.
        """
        QtGui.QWidget.update(self)
        self._canvas.update()


class QtSceneCanvas(QtCanvas):
    """ Convenience class embedding a vispy SceneCanvas inside a QWidget.
    
    See QtCanvas.
    """
    def __init__(self, parent=None, **kwargs):
        from ..scene.canvas import SceneCanvas
        QtCanvas.__init__(self, parent, canvas=SceneCanvas, **kwargs)
