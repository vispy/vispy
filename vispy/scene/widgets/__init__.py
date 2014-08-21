# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
The vispy.scene.widgets namespace provides a range of widgets to allow
user interaction. Widgets are rectangular Visual objects such as buttons
and sliders.
"""
__all__ = ['Widget', 'ViewBox', 'Grid']

from .grid import Grid  # noqa
from .viewbox import ViewBox  # noqa
from .widget import Widget  # noqa
