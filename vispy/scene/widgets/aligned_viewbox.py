# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from typing import Tuple

from enum import unique, auto, IntEnum

from .viewbox import ViewBox


@unique
class Alignment(IntEnum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class AlignedViewBox(ViewBox):
    """
    Provides a similar widget as ViewBox. However, it is possible to automatically align the
    widget to a chosen corner of the window.

    Parameters
    ----------
    alignment : instance of Alignment
        Defines to which corner of the window this widget should align.
    **kwargs : dict
        Extra keyword arguments to pass to `ViewBox`.
    """

    pos: Tuple[int, int]  # only defined for type-hinting

    def __init__(self, alignment: Alignment = Alignment.TOP_LEFT, **kwargs):
        self._alginment = alignment
        super().__init__(**kwargs)

    def on_resize(self, event) -> None:
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        super().on_resize(event)

        if self.parent is None:
            return

        parent_width, parent_height = self.parent.size

        bounds = self.get_scene_bounds()
        width = bounds[0][1] - bounds[0][0]
        height = bounds[1][1] - bounds[1][0]

        if self._alginment == Alignment.TOP_LEFT:
            return
        elif self._alginment == Alignment.BOTTOM_LEFT:
            y = parent_height - height
            self.pos = (self.pos[0], y)
        elif self._alginment == Alignment.TOP_RIGHT:
            x = parent_width - width
            self.pos = (x, self.pos[1])
        else:
            y = parent_height - height
            x = parent_width - width
            self.pos = (x, y)
