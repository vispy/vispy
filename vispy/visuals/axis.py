# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from .visual import Visual
from .line import LineVisual
from .text import TextVisual

# XXX TODO list (see code, plus):
# 1. Automated tick direction?
# 2. Expand to 3D (only 2D supported currently)
# 3. Input validation
# 4. Property support
# 5. Reactivity to resizing (current tick lengths grow/shrink w/zoom)
# 6. Improve tick label naming (str(x) is not good) and tick selection


class AxisVisual(Visual):
    """Axis visual

    Parameters
    ----------
    pos : array
        Co-ordinates of start and end of the axis.
    domain : tuple
        The data values at the beginning and end of the axis, used for tick
        labels. i.e. (5, 10) means the axis starts at 5 and ends at 10. Default
        is (0, 1).
    tick_direction : array
        The tick direction to use (in document coordinates).
    scale_type : str
        The type of scale. For now only 'linear' is supported.
    axis_color : tuple
        RGBA values for the axis colour. Default is black.
    tick_color : tuple
        RGBA values for the tick colours. The colour for the major and minor
        ticks is currently fixed to be the same. Default is a dark grey.
    **kwargs : dict
        Keyword arguments to pass to `Visual`.
    """
    def __init__(self, pos, domain=(0., 1.), tick_direction=(-1., 0.),
                 scale_type="linear", axis_color=(1, 1, 1),
                 tick_color=(0.7, 0.7, 0.7), **kwargs):
        Visual.__init__(self, **kwargs)
        if scale_type != 'linear':
            raise NotImplementedError('only linear scaling is currently '
                                      'supported')
        self.pos = np.array(pos, float)
        self.domain = domain
        self.tick_direction = np.array(tick_direction, float)
        self.tick_direction = self.tick_direction
        self.scale_type = scale_type
        self.axis_color = axis_color
        self.tick_color = tick_color

        self.minor_tick_length = 5  # px
        self.major_tick_length = 10  # px
        self.label_margin = 5  # px

        self._text = None
        self._line = None
        self._ticks = None

    @property
    def _vec(self):
        """Vector in the direction of the axis line"""
        return self.pos[1] - self.pos[0]

    def draw(self, transforms):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """

        # Initialize two LineVisuals - one for the axis line, one for ticks
        if self._text is None:
            major_tick_fractions, minor_tick_fractions, tick_labels = \
                self._get_tick_frac_labels()

            tick_pos, tick_label_pos, anchors = self._get_tick_positions(
                major_tick_fractions, minor_tick_fractions, transforms)

            self._line = LineVisual(pos=self.pos, color=self.axis_color,
                                    method='gl', width=3.0)
            self._ticks = LineVisual(pos=tick_pos, color=self.tick_color,
                                     method='gl', width=2.0,
                                     connect='segments')
            self._text = TextVisual(list(tick_labels), pos=tick_label_pos,
                                    font_size=8, color='w',
                                    anchor_x=anchors[0], anchor_y=anchors[1])

        self._line.draw(transforms)
        self._ticks.draw(transforms)
        self._text.draw(transforms)

    def bounds(self, mode, axis):
        """Get the bounds

        Parameters
        ----------
        mode : str
            Describes the type of boundary requested. Can be "visual", "data",
            or "mouse".
        axis : 0, 1, 2
            The axis along which to measure the bounding values, in
            x-y-z order.
        """
        assert axis in (0, 1, 2)
        if axis == 2:
            return (0., 0.)
        # now axis in (0, 1)
        return self.pos[:, axis].min(), self.pos[:, axis].max()

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions,
                            transforms):
        # transform our tick direction to document coords
        visual_to_document = transforms.visual_to_document
        direction = visual_to_document.map(np.array([[0., 0.],
                                                     self.tick_direction],
                                                    float))
        direction = (direction[1] - direction[0])[:2]
        direction /= np.linalg.norm(direction)
        # use the document (pixel) coord system to set text anchors
        anchors = []
        if direction[0] < 0:
            anchors.append('right')
        elif direction[0] > 0:
            anchors.append('left')
        else:
            anchors.append('center')
        if direction[1] < 0:
            anchors.append('bottom')
        elif direction[1] > 0:
            anchors.append('top')
        else:
            anchors.append('middle')

        # now figure out the tick positions in visual (data) coords
        vectors = np.array([[0., 0.],
                            direction * self.minor_tick_length,
                            direction * self.major_tick_length,
                            direction * (self.major_tick_length +
                                         self.label_margin)], float)
        vectors = visual_to_document.imap(vectors)[:, :2]
        minor_vector = vectors[1] - vectors[0]
        major_vector = vectors[2] - vectors[0]
        label_vector = vectors[3] - vectors[0]

        major_origins, major_endpoints = self._tile_ticks(
            major_tick_fractions, major_vector)

        minor_origins, minor_endpoints = self._tile_ticks(
            minor_tick_fractions, minor_vector)

        tick_label_pos = major_origins + label_vector

        num_major = len(major_tick_fractions)
        num_minor = len(minor_tick_fractions)

        c = np.empty([(num_major + num_minor) * 2, 2])

        c[0:(num_major-1)*2+1:2] = major_origins
        c[1:(num_major-1)*2+2:2] = major_endpoints
        c[(num_major-1)*2+2::2] = minor_origins
        c[(num_major-1)*2+3::2] = minor_endpoints

        return c, tick_label_pos, anchors

    def _tile_ticks(self, frac, tickvec):
        """Tiles tick marks along the axis."""
        origins = np.tile(self._vec, (len(frac), 1))
        origins = self.pos[0].T + (origins.T*frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self):
        # This conditional is currently unnecessary since we only support
        # linear, but eventually we will support others so we leave it in
        if (self.scale_type == 'linear'):

            major_num = 11  # maximum number of major ticks
            minor_num = 4   # maximum number of minor ticks per major division

            major, majstep = np.linspace(0, 1, num=major_num, retstep=True)

            # XXX TODO: this should be better than just str(x)
            labels = [str(x) for x in np.interp(major, [0, 1], self.domain)]

            # XXX TODO: make these nice numbers only
            # - and faster! Potentially could draw in linspace across the whole
            # axis and render them before the major ticks, so the overlap
            # gets hidden. Might be messy. Benchmark trade-off of extra GL
            # versus extra NumPy.
            minor = []
            for i in np.nditer(major[:-1]):
                minor.extend(np.linspace(i, (i + majstep),
                             (minor_num + 2))[1:-1])
        # elif (self.scale_type == 'logarithmic'):
        #     return NotImplementedError
        # elif (self.scale_type == 'power'):
        #     return NotImplementedError
        return major, minor, labels
