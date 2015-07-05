# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from .widget import Widget
from ...visuals import TextVisual


class Label(Widget):
    """Label widget

    Parameters
    ----------
    text : str
        The label.
    rotation : float
        The rotation of the label.
    **kwargs : dict
        Keyword arguments to pass to TextVisual.
    """
    def __init__(self, text, rotation=0., **kwargs):
        self._text_visual = TextVisual(text=text, rotation=rotation, **kwargs)
        self.rotation = rotation
        Widget.__init__(self)
        self.add_subvisual(self._text_visual)
        self._set_pos()
        
    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._set_pos()
        
    def _set_pos(self):
        self._text_visual.pos = self.rect.center
        
    @property
    def text(self):
        return self._text_visual.text
    
    @text.setter
    def text(self, t):
        self._text_visual.text = t
