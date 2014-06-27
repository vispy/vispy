# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ...util import event
from ..entity import Entity

"""
API Issues to work out:

  * Need Visual.bounds() as described here:
    https://github.com/vispy/vispy/issues/141

"""


class Visual(Entity):
    """
    Abstract class representing a drawable object.

    At a minimum, Visual subclasses should extend the draw() method. 

    Events:

    update : Event
        Emitted when the visual has changed and needs to be redrawn.
    bounds_change : Event
        Emitted when the bounds of the visual have changed.

    """

    def __init__(self, parent=None, **kwds):
        Entity.__init__(self, parent, **kwds)
        
        # Add event for bounds changing
        self.events.add(bounds_change=event.Event)

    def _update(self):
        """
        This method is called internally whenever the Visual needs to be 
        redrawn. By default, it emits the update event.
        """
        self.events.update()

    def draw(self, event=None):
        """
        Draw this visual now.
        The default implementation does nothing.
        """
        pass

    def bounds(self, axis):
        """
        Return the boundaries of this visual along *axis*, which may be 0, 1, 
        or 2. 
        
        This is used primarily to allow automatic ViewBox zoom/pan.
        By default, this method returns None which indicates the object should 
        be ignored for automatic zooming along *axis*.
        
        A scenegraph may also use this information to cull visuals from the
        display list.
        """
        return None
