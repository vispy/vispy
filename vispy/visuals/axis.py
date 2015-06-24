# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from .visual import CompoundVisual
from .line import LineVisual
from .text import TextVisual

# XXX TODO list (see code, plus):
# 1. Automated tick direction?
# 2. Expand to 3D (only 2D supported currently)
# 3. Input validation
# 4. Property support
# 5. Reactivity to resizing (current tick lengths grow/shrink w/zoom)
# 6. Improve tick label naming (str(x) is not good) and tick selection


class AxisVisual(CompoundVisual):
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
    def __init__(self, pos=None, domain=(0., 1.), tick_direction=(-1., 0.),
                 scale_type="linear", axis_color=(1, 1, 1),
                 tick_color=(0.7, 0.7, 0.7)):
        if scale_type != 'linear':
            raise NotImplementedError('only linear scaling is currently '
                                      'supported')
        self._pos = None
        self._domain = None
        self.ticker = Ticker(self)
        self.tick_direction = np.array(tick_direction, float)
        self.tick_direction = self.tick_direction
        self.scale_type = scale_type
        self.axis_color = axis_color
        self.tick_color = tick_color

        self.minor_tick_length = 5  # px
        self.major_tick_length = 10  # px
        self.label_margin = 5  # px
        
        self._need_update = True

        CompoundVisual.__init__(self, [])
        
        self._line = LineVisual(method='gl', width=3.0)
        self._ticks = LineVisual(method='gl', width=2.0, connect='segments')
        self._text = TextVisual(font_size=8, color='w')
        self.add_subvisual(self._line)
        self.add_subvisual(self._ticks)
        self.add_subvisual(self._text)

        if pos is not None:
            self.pos = pos
        self.domain = domain

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, pos):
        self._pos = np.array(pos, float)
        self._need_update = True
        self.update()

    @property
    def domain(self):
        return self._domain
    
    @domain.setter
    def domain(self, d):
        if d != self._domain:
            self._domain = d
            self._need_update = True
            self.update()

    @property
    def _vec(self):
        """Vector in the direction of the axis line"""
        return self.pos[1] - self.pos[0]

    def _update_subvisuals(self):
        tick_pos, labels, label_pos, anchors = self.ticker.get_update()

        self._line.set_data(pos=self.pos, color=self.axis_color)
        self._ticks.set_data(pos=tick_pos, color=self.tick_color)
        self._text.text = list(labels)
        self._text.pos = label_pos
        self._text.anchors = anchors

        self._need_update = False

    def _prepare_draw(self, view):
        if self._pos is None:
            return False
        if self._need_update:
            self._update_subvisuals()

    def _compute_bounds(self, axis, view):
        if axis == 2:
            return (0., 0.)
        # now axis in (0, 1)
        return self.pos[:, axis].min(), self.pos[:, axis].max()


class Ticker(object):
    def __init__(self, axis):
        self.axis = axis
        
    def get_update(self):
        major_tick_fractions, minor_tick_fractions, tick_labels = \
            self._get_tick_frac_labels()
        tick_pos, label_pos, anchors = self._get_tick_positions(
            major_tick_fractions, minor_tick_fractions)
        return tick_pos, tick_labels, label_pos, anchors

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions):
        # transform our tick direction to document coords
        trs = self.axis.transforms
        visual_to_document = trs.get_transform('visual', 'document')
        direction = visual_to_document.map(np.array([[0., 0.],
                                                     self.axis.tick_direction],
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
                            direction * self.axis.minor_tick_length,
                            direction * self.axis.major_tick_length,
                            direction * (self.axis.major_tick_length +
                                         self.axis.label_margin)], float)
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
        origins = np.tile(self.axis._vec, (len(frac), 1))
        origins = self.axis.pos[0].T + (origins.T*frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self):
        # This conditional is currently unnecessary since we only support
        # linear, but eventually we will support others so we leave it in
        if (self.axis.scale_type == 'linear'):

            major_num = 11  # maximum number of major ticks
            minor_num = 4   # maximum number of minor ticks per major division

            major, majstep = np.linspace(0, 1, num=major_num, retstep=True)

            # XXX TODO: this should be better than just str(x)
            labels = [str(x) for x in 
                      np.interp(major, [0, 1], self.axis.domain)]

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
