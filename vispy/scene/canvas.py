# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Implementation of a canvas that has a ViewBox so it can hold a scene graph.
"""

from __future__ import division

from .base import ViewBox
from .. import app, gloo
from ..util import logger
gl = gloo.gl


class CanvasWithScene(app.Canvas):
    """Provide a window or widget that the root scene can be rendered to

    The generated window or widget has a ViewBox instance for which
    the size is kept in sync with the underlying GL widget.

    Parameters
    ----------
    *args, **kwargs : arguments
        These are passed directly to app.Canvas.
    """
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self._viewbox = ViewBox()

    @property
    def viewbox(self):
        """The root viewbox object for this canvas.
        """
        return self._viewbox

    def on_initialize(self, event):
        # Initialize opengl
        gl.glClearColor(0, 0, 0, 1)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

    def on_resize(self, event):
        self._viewbox.transform[0, 0] = event.size[0]
        self._viewbox.transform[1, 1] = event.size[1]

    def on_paint(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        logger.debug('Painting ...')

        # Draw viewbox
        self._process_entity_count = 0
        self._viewbox.process(self, 'draw')
        logger.debug('Entity count %s' % self._process_entity_count)

    def on_mouse_move(self, event):
        # todo: we need a proper way to deal with events
        self._viewbox.camera.on_mouse_move(event)
