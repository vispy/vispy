# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import sys

from ..visuals.visual import Visual
from ..util.logs import logger, _handle_exception
from ..util.profiler import Profiler


class DrawingSystem(object):
    """ Simple implementation of a drawing engine. There is one system
    per viewbox.

    """
    def process(self, event, node):
        prof = Profiler(str(node))
        # Draw this node if it is a visual
        if isinstance(node, Visual) and node.visible:
            try:
                node.draw(event)
                prof('draw')
            except Exception:
                # get traceback and store (so we can do postmortem
                # debugging)
                _handle_exception(False, 'reminders', self, node=node)

        # Processs children recursively, unless the node has already
        # handled them.
        for sub_node in node.children:
            if sub_node in event.handled_children:
                continue
            event.push_node(sub_node)
            try:
                self.process(event, sub_node)
            finally:
                event.pop_node()
            prof('process child %s', sub_node)


class MouseInputSystem(object):
    def process(self, event, node):
        # For simplicity, this system delivers the event to each node
        # in the scenegraph, except for widgets that are not under the 
        # press_event. 
        # TODO: This eventually should be replaced with a picking system.
        
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
                    self.process(event, sub_node)
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
