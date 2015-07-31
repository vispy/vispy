# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event


class SceneMouseEvent(Event):
    """ Represents a mouse event that occurred on a SceneCanvas. This event is
    delivered to all entities whose mouse interaction area is under the event.
    """
    def __init__(self, event, visual):
        self.mouse_event = event
        self.visual = visual
        Event.__init__(self, type=event.type)

    @property
    def visual(self):
        return self._visual
    
    @visual.setter
    def visual(self, v):
        self._visual = v
        self._pos = None

    @property
    def pos(self):
        """ The position of this event in the local coordinate system of the
        visual.
        """
        if self._pos is None:
            tr = self.visual.get_transform('canvas', 'visual')
            self._pos = tr.map(self.mouse_event.pos)
        return self._pos

    @property
    def last_event(self):
        """ The mouse event immediately prior to this one. This
        property is None when no mouse buttons are pressed.
        """
        if self.mouse_event.last_event is None:
            return None
        ev = self.copy()
        ev.mouse_event = self.mouse_event.last_event
        return ev

    @property
    def press_event(self):
        """ The mouse press event that initiated a mouse drag, if any.
        """
        if self.mouse_event.press_event is None:
            return None
        ev = self.copy()
        ev.mouse_event = self.mouse_event.press_event
        return ev

    @property
    def button(self):
        """ The button pressed or released on this event.
        """
        return self.mouse_event.button

    @property
    def buttons(self):
        """ A list of all buttons currently pressed on the mouse.
        """
        return self.mouse_event.buttons

    @property
    def delta(self):
        """ The increment by which the mouse wheel has moved.
        """
        return self.mouse_event.delta

    def copy(self):
        ev = self.__class__(self.mouse_event, self.visual)
        return ev
