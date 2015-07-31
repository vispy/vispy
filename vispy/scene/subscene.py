# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .node import Node


class SubScene(Node):
    """A Node subclass that serves as a marker and parent node for certain
    branches of the scenegraph.
    
    SubScene nodes are used as the top-level node for the internal scenes of
    a canvas and a view box.
    """
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        self.document = self
