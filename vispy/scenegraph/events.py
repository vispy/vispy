# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event

class SceneMouseEvent(Event):
    def __init__(self, event):
        self.mouse_event = event
        super(SceneMouseEvent, self).__init__(type='scene_'+event.type)
        
    
