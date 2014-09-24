# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import sys

from ..visuals.visual import Visual
from ..util.logs import logger, _handle_exception


class DrawingSystem(object):
    """ Simple implementation of a drawing engine. There is one system
    per viewbox.

    """
    def process(self, event, subscene):
        # Iterate over entities
        #assert isinstance(subscene, SubScene)  # LC: allow any part of the
                                                #     scene to be drawn
        self._process_node(event, subscene)

    def _process_node(self, event, node):
        if isinstance(node, Visual):
            try:
                node.draw(event)
            except Exception:
                # get traceback and store (so we can do postmortem
                # debugging)
                _handle_exception(False, 'reminders', self, node=node)

        # Processs children; recurse.
        if not event.children_handled:
            for sub_node in node.children:
                event.push_node(sub_node)
                try:
                    self._process_node(event, sub_node)
                finally:
                    event.pop_node()


class MouseInputSystem(object):
    def process(self, event, subscene):
        # For simplicity, this system delivers the event to each node
        # in the scenegraph, except for widgets that are not under the 
        # press_event. 
        # TODO: 
        #  1. This eventually should be replaced with a picking system.
        #  2. We also need to ensure that if one node accepts a press 
        #     event, it will also receive all subsequent mouse events
        #     until the button is released.
        
        self._process_node(event, subscene)
    
    def _process_node(self, event, node):
        # Push node and set its total transform
        #event.push_node(node)

        from .widgets.widget import Widget
        if isinstance(node, Widget):
            # widgets are rectangular; easy to do mouse collision 
            # testing
            if event.press_event is None:
                deliver = node.rect.contains(*event.pos[:2])
            else:
                deliver = node.rect.contains(*event.press_event.pos[:2])
        else:
            deliver = True
                
        if deliver:
            for sub_node in node.children:
                event.push_node(sub_node)
                try:
                    self._process_node(event, sub_node)
                finally:
                    event.pop_node()
                if event.handled:
                    break
            if not event.handled:
                try:
                    getattr(node.events, event.type)(event)
                except Exception:
                    # get traceback and store (so we can do postmortem
                    # debugging)
                    type, value, tb = sys.exc_info()
                    tb = tb.tb_next  # Skip *this* frame
                    sys.last_type = type
                    sys.last_value = value
                    sys.last_traceback = tb
                    del tb  # Get rid of it in this namespace
                    # Handle
                    logger.log_exception()
                    logger.warning("Error handling mouse event for node %s" %
                                   node)
                    
        #event.pop_node()
