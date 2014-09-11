# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from . import use_app
try:
    app_object = use_app('pyqt4')
except Exception:
    app_object = use_app('pyside')

from .backends._qt import QtGui


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
    
    def __init__(self, parent=None, canvas=None, **kwds):
        from .canvas import Canvas
        if canvas is None:
            canvas = Canvas
        if issubclass(canvas, Canvas):
            canvas = canvas(**kwds)
        elif len(**kwds) > 0:
            raise TypeError('Invalid keyword arguments: %s' % 
                            list(kwds.keys()))
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


class QtSceneCanvas(QtCanvas):
    """ Convenience class embedding a vispy SceneCanvas inside a QWidget.
    
    See QtCanvas.
    """
    def __init__(self, parent=None, **kwds):
        from ..scene.canvas import SceneCanvas
        QtCanvas.__init__(self, parent, canvas=SceneCanvas, **kwds)
