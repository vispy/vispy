# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import math
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
    """Class to determine tick marks

    Parameters
    ----------
    axis : instance of AxisVisual
        The AxisVisual to generate ticks for.
    """

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
        """Get the major ticks, minor ticks, and major labels"""
        major_num = 11  # number of major ticks
        minor_num = 4  # number of minor ticks per major division
        if (self.axis.scale_type == 'linear'):
            major, majstep = np.linspace(0, 1, num=major_num, retstep=True)
            labels = ['%g' % x
                      for x in np.interp(major, [0, 1], self.axis.domain)]
            minor = []
            for i in major[:-1]:
                minor.extend(np.linspace(i, (i + majstep),
                             (minor_num + 2))[1:-1])
        elif self.axis.scale_type == 'logarithmic':
            return NotImplementedError
        elif self.axis.scale_type == 'power':
            return NotImplementedError
        return major, minor, labels


# Translated from matplotlib

class MaxNLocator(object):
    """
    Select no more than N intervals at nice locations.
    """
    def __init__(self, nbins=10, steps=None, trim=True, integer=False,
                 symmetric=False, prune=None):
            """
            Keyword args:
            *nbins*
                Maximum number of intervals; one less than max number of ticks.
            *steps*
                Sequence of nice numbers starting with 1 and ending with 10;
                e.g., [1, 2, 4, 5, 10]
            *integer*
                If True, ticks will take only integer values.
            *symmetric*
                If True, autoscaling will result in a range symmetric
                about zero.
            *prune*
                ['lower' | 'upper' | 'both' | None]
                Remove edge ticks -- useful for stacked or ganged plots
                where the upper tick of one axes overlaps with the lower
                tick of the axes above it.
                If prune=='lower', the smallest tick will
                be removed.  If prune=='upper', the largest tick will be
                removed.  If prune=='both', the largest and smallest ticks
                will be removed.  If prune==None, no ticks will be removed.
            """
            self._nbins = int(nbins)
            self._trim = trim
            self._integer = integer
            self._symmetric = symmetric
            if prune is not None and prune not in ['upper', 'lower', 'both']:
                raise ValueError(
                    "prune must be 'upper', 'lower', 'both', or None")
            self._prune = prune
            if steps is None:
                steps = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
            else:
                if int(steps[-1]) != 10:
                    steps = list(steps)
                    steps.append(10)
            self._steps = steps
            self._integer = integer
            if self._integer:
                self._steps = [n for n in self._steps
                               if divmod(n, 1)[1] < 0.001]

    def bin_boundaries(self, vmin, vmax):
        nbins = self._nbins
        scale, offset = scale_range(vmin, vmax, nbins)
        if self._integer:
            scale = max(1, scale)
        vmin = vmin - offset
        vmax = vmax - offset
        raw_step = (vmax - vmin) / nbins
        scaled_raw_step = raw_step / scale
        best_vmax = vmax
        best_vmin = vmin

        for step in self._steps:
            if step < scaled_raw_step:
                continue
            step *= scale
            best_vmin = step * divmod(vmin, step)[0]
            best_vmax = best_vmin + step * nbins
            if (best_vmax >= vmax):
                break
        if self._trim:
            extra_bins = int(divmod((best_vmax - vmax), step)[0])
            nbins -= extra_bins
        return (np.arange(nbins + 1) * step + best_vmin + offset)

    def __call__(self):
        vmin, vmax = self.axis.get_view_interval()
        return self.tick_values(vmin, vmax)

    def tick_values(self, vmin, vmax):
        locs = self.bin_boundaries(vmin, vmax)
        prune = self._prune
        if prune == 'lower':
            locs = locs[1:]
        elif prune == 'upper':
            locs = locs[:-1]
        elif prune == 'both':
            locs = locs[1:-1]
        return locs

    def view_limits(self, dmin, dmax):
        if self._symmetric:
            maxabs = max(abs(dmin), abs(dmax))
            dmin = -maxabs
            dmax = maxabs
        return np.take(self.bin_boundaries(dmin, dmax), [0, -1])


def scale_range(vmin, vmax, n=1, threshold=100):
    dv = abs(vmax - vmin)
    if dv == 0:     # maxabsv == 0 is a special case of this.
        return 1.0, 0.0
        # Note: this should never occur because
        # vmin, vmax should have been checked by nonsingular(),
        # and spread apart if necessary.
    meanv = 0.5 * (vmax + vmin)
    if abs(meanv) / dv < threshold:
        offset = 0
    elif meanv > 0:
        ex = divmod(math.log10(meanv), 1)[0]
        offset = 10 ** ex
    else:
        ex = divmod(math.log10(-meanv), 1)[0]
        offset = -10 ** ex
    ex = divmod(math.log10(dv / n), 1)[0]
    scale = 10 ** ex
    return scale, offset


class AutoLocator(MaxNLocator):
    def __init__(self):
        MaxNLocator.__init__(self, nbins=9, steps=[1, 2, 5, 10])
