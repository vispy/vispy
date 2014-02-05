# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ...visuals import PointsVisual
from ..base import Entity


class PointsEntity(Entity):

    """ An entity that shows a random set of points.
    """

    Visual = PointsVisual

    def __init__(self, parent=None, N=1000):
        Entity.__init__(self, parent, N=N)
