# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import math

import numpy as np

from .visual import CompoundVisual, updating_property
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
    text_color : Color
        The color to use for drawing tick and axis labels
    minor_tick_length : float
        The length of minor ticks, in pixels
    major_tick_length : float
        The length of major ticks, in pixels
    tick_width : float
        Line width for the ticks
    tick_label_margin : float
        Margin between ticks and tick labels
    tick_font_size : float
        The font size to use for rendering tick labels.
    axis_width : float
        Line width for the axis
    axis_label : str
        Text to use for the axis label
    axis_label_margin : float
        Margin between ticks and axis labels
    axis_font_size : float
        The font size to use for rendering axis labels.
    font_size : float
        Font size for both the tick and axis labels. If this is set,
        tick_font_size and axis_font_size are ignored.
    anchors : iterable
        A 2-element iterable (tuple, list, etc.) giving the horizontal and
        vertical alignment of the tick labels. The first element should be one
        of 'left', 'center', or 'right', and the second element should be one
        of 'bottom', 'middle', or 'top'. If this is not specified, it is
        determined automatically.
    """

    def __init__(self, pos=None, domain=(0., 1.), 
                 tick_direction=(-1., 0.), 
                 scale_type="linear", 
                 axis_color=(1, 1, 1), 
                 tick_color=(0.7, 0.7, 0.7), 
                 text_color='w', 
                 minor_tick_length=5, 
                 major_tick_length=10, 
                 tick_width=2, 
                 tick_label_margin=12, 
                 tick_font_size=8, 
                 axis_width=3, 
                 axis_label=None, 
                 axis_label_margin=35, 
                 axis_font_size=10, 
                 font_size=None, 
                 anchors=None):

        if scale_type != 'linear':
            raise NotImplementedError('only linear scaling is currently '
                                      'supported')

        if font_size is not None:
            tick_font_size = font_size
            axis_font_size = font_size

        self._pos = None
        self._domain = None

        # If True, then axis stops at the first / last major tick.
        # If False, then axis extends to edge of *pos*
        # (private until we come up with a better name for this)
        self._stop_at_major = (False, False)

        self.ticker = Ticker(self, anchors=anchors)
        self.tick_direction = np.array(tick_direction, float)
        self.scale_type = scale_type

        self._minor_tick_length = minor_tick_length  # px
        self._major_tick_length = major_tick_length  # px
        self._tick_label_margin = tick_label_margin  # px
        self._axis_label_margin = axis_label_margin  # px

        self._axis_label = axis_label

        self._need_update = True

        self._line = LineVisual(method='gl', width=axis_width, antialias=True,
                                color=axis_color)
        self._ticks = LineVisual(method='gl', width=tick_width,
                                 connect='segments', antialias=True,
                                 color=tick_color)

        self._text = TextVisual(font_size=tick_font_size, color=text_color)
        self._axis_label_vis = TextVisual(font_size=axis_font_size,
                                          color=text_color)
        CompoundVisual.__init__(self, [self._line, self._text, self._ticks,
                                       self._axis_label_vis])
        if pos is not None:
            self.pos = pos
        self.domain = domain

    @property
    def text_color(self):
        return self._text.color

    @text_color.setter
    def text_color(self, value):
        self._text.color = value
        self._axis_label_vis.color = value

    @property
    def axis_color(self):
        return self._line.color

    @axis_color.setter
    def axis_color(self, value):
        self._line.set_data(color=value)

    @property
    def axis_width(self):
        return self._line.width

    @axis_width.setter
    def axis_width(self, value):
        self._line.set_data(width=value)

    @property
    def tick_color(self):
        return self._ticks.color

    @tick_color.setter
    def tick_color(self, value):
        self._ticks.set_data(color=value)

    @property
    def tick_width(self):
        return self._ticks.width

    @tick_width.setter
    def tick_width(self, value):
        self._ticks.set_data(width=value)

    @property
    def tick_font_size(self):
        return self._text.font_size

    @tick_font_size.setter
    def tick_font_size(self, value):
        self._text.font_size = value

    @updating_property
    def tick_direction(self):
        """The tick direction to use (in document coordinates)."""

    @tick_direction.setter
    def tick_direction(self, tick_direction):
        self._tick_direction = np.array(tick_direction, float)

    @property
    def axis_font_size(self):
        return self._axis_label_vis.font_size

    @axis_font_size.setter
    def axis_font_size(self, value):
        self._axis_label_vis.font_size = value

    @updating_property
    def domain(self):
        """The data values at the beginning and end of the axis, used for tick labels."""

    @updating_property
    def axis_label(self):
        """Text to use for the axis label."""

    @updating_property
    def pos(self):
        """Co-ordinates of start and end of the axis."""

    @pos.setter
    def pos(self, pos):
        self._pos = np.array(pos, float)

    @updating_property
    def minor_tick_length(self):
        """The length of minor ticks, in pixels"""

    @updating_property
    def major_tick_length(self):
        """The length of major ticks, in pixels"""

    @updating_property
    def tick_label_margin(self):
        """Margin between ticks and tick labels"""

    @updating_property
    def axis_label_margin(self):
        """Margin between ticks and axis labels"""

    @property
    def _vec(self):
        """Vector in the direction of the axis line"""
        return self.pos[1] - self.pos[0]

    def _update_subvisuals(self):
        tick_pos, labels, tick_label_pos, anchors, axis_label_pos = \
            self.ticker.get_update()

        self._line.set_data(pos=self.pos, color=self.axis_color)
        self._ticks.set_data(pos=tick_pos, color=self.tick_color)
        self._text.text = list(labels)
        self._text.pos = tick_label_pos
        self._text.anchors = anchors
        if self.axis_label is not None:
            self._axis_label_vis.text = self.axis_label
            self._axis_label_vis.pos = axis_label_pos
        self._need_update = False

    def _prepare_draw(self, view):
        if self._pos is None:
            return False
        if self.axis_label is not None:
            self._axis_label_vis.rotation = self._rotation_angle
        if self._need_update:
            self._update_subvisuals()

    @property
    def _rotation_angle(self):
        """Determine the rotation angle of the axis as projected onto the canvas."""
        # TODO: make sure we only call get_transform if the transform for
        # the line is updated
        tr = self._line.get_transform(map_from='visual', map_to='canvas')
        trpos = tr.map(self.pos)
        # Normalize homogeneous coordinates
        # trpos /= trpos[:, 3:]
        x1, y1, x2, y2 = trpos[:, :2].ravel()
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        return math.degrees(math.atan2(y2-y1, x2-x1))

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

    def __init__(self, axis, anchors=None):
        self.axis = axis
        self._anchors = anchors

    def get_update(self):
        major_tick_fractions, minor_tick_fractions, tick_labels = \
            self._get_tick_frac_labels()
        tick_pos, tick_label_pos, axis_label_pos, anchors = \
            self._get_tick_positions(major_tick_fractions,
                                     minor_tick_fractions)
        return tick_pos, tick_labels, tick_label_pos, anchors, axis_label_pos

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions):
        # tick direction is defined in visual coords, but use document
        # coords to determine the tick length
        trs = self.axis.transforms
        visual_to_document = trs.get_transform('visual', 'document')
        direction = np.array(self.axis.tick_direction)
        direction /= np.linalg.norm(direction)

        if self._anchors is None:
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
        else:
            anchors = self._anchors

        # now figure out the tick positions in visual (data) coords
        doc_unit = visual_to_document.map([[0, 0], direction[:2]])
        doc_unit = doc_unit[1] - doc_unit[0]
        doc_len = np.linalg.norm(doc_unit)

        vectors = np.array([[0., 0.],
                            direction * self.axis.minor_tick_length / doc_len,
                            direction * self.axis.major_tick_length / doc_len,
                            direction * (self.axis.major_tick_length +
                                         self.axis.tick_label_margin) / doc_len
                            ],
                           dtype=float)
        minor_vector = vectors[1] - vectors[0]
        major_vector = vectors[2] - vectors[0]
        label_vector = vectors[3] - vectors[0]

        axislabel_vector = direction * (self.axis.major_tick_length +
                                        self.axis.axis_label_margin) / doc_len

        major_origins, major_endpoints = self._tile_ticks(
            major_tick_fractions, major_vector)

        minor_origins, minor_endpoints = self._tile_ticks(
            minor_tick_fractions, minor_vector)

        tick_label_pos = major_origins + label_vector

        axis_label_pos = 0.5 * (self.axis.pos[0] +
                                self.axis.pos[1]) + axislabel_vector

        num_major = len(major_tick_fractions)
        num_minor = len(minor_tick_fractions)

        c = np.empty([(num_major + num_minor) * 2, 2])

        c[0:(num_major-1)*2+1:2] = major_origins
        c[1:(num_major-1)*2+2:2] = major_endpoints
        c[(num_major-1)*2+2::2] = minor_origins
        c[(num_major-1)*2+3::2] = minor_endpoints

        return c, tick_label_pos, axis_label_pos, anchors

    def _tile_ticks(self, frac, tickvec):
        """Tiles tick marks along the axis."""
        origins = np.tile(self.axis._vec, (len(frac), 1))
        origins = self.axis.pos[0].T + (origins.T*frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self):
        """Get the major ticks, minor ticks, and major labels"""
        minor_num = 4  # number of minor ticks per major division
        if (self.axis.scale_type == 'linear'):
            domain = self.axis.domain
            if domain[1] < domain[0]:
                flip = True
                domain = domain[::-1]
            else:
                flip = False
            offset = domain[0]
            scale = domain[1] - domain[0]

            transforms = self.axis.transforms
            length = self.axis.pos[1] - self.axis.pos[0]  # in logical coords
            n_inches = np.sqrt(np.sum(length ** 2)) / transforms.dpi

            major = _get_ticks_talbot(domain[0], domain[1], n_inches, 2)

            labels = ['%g' % x for x in major]
            majstep = major[1] - major[0]
            minor = []
            minstep = majstep / (minor_num + 1)
            minstart = 0 if self.axis._stop_at_major[0] else -1
            minstop = -1 if self.axis._stop_at_major[1] else 0
            for i in range(minstart, len(major) + minstop):
                maj = major[0] + i * majstep
                minor.extend(np.linspace(maj + minstep,
                                         maj + majstep - minstep,
                                         minor_num))
            major_frac = major - offset
            minor_frac = np.array(minor) - offset
            if scale != 0:  # maybe something better to do here?
                major_frac /= scale
                minor_frac /= scale
            use_mask = (major_frac > -0.0001) & (major_frac < 1.0001)
            major_frac = major_frac[use_mask]
            labels = [l for li, l in enumerate(labels) if use_mask[li]]
            minor_frac = minor_frac[(minor_frac > -0.0001) &
                                    (minor_frac < 1.0001)]
            # Flip ticks coordinates if necessary :
            if flip:
                major_frac = 1 - major_frac
                minor_frac = 1 - minor_frac
        elif self.axis.scale_type == 'logarithmic':
            return NotImplementedError
        elif self.axis.scale_type == 'power':
            return NotImplementedError
        return major_frac, minor_frac, labels


# #############################################################################
# Translated from matplotlib

class MaxNLocator(object):
    """Select no more than N intervals at nice locations."""

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
            steps = [1, 2, 2.5, 3, 4, 5, 6, 8, 10]
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
        ex = divmod(np.log10(meanv), 1)[0]
        offset = 10 ** ex
    else:
        ex = divmod(np.log10(-meanv), 1)[0]
        offset = -10 ** ex
    ex = divmod(np.log10(dv / n), 1)[0]
    scale = 10 ** ex
    return scale, offset


# #############################################################################
# Tranlated from http://www.justintalbot.com/research/axis-labeling/

# See "An Extension of Wilkinson's Algorithm for Positioning Tick Labels
# on Axes" # by Justin Talbot, Sharon Lin, and Pat Hanrahan, InfoVis 2010.


def _coverage(dmin, dmax, lmin, lmax):
    return 1 - 0.5 * ((dmax - lmax) ** 2 +
                      (dmin - lmin) ** 2) / (0.1 * (dmax - dmin)) ** 2


def _coverage_max(dmin, dmax, span):
    range_ = dmax - dmin
    if span <= range_:
        return 1.
    else:
        half = (span - range_) / 2.0
        return 1 - half ** 2 / (0.1 * range_) ** 2


def _density(k, m, dmin, dmax, lmin, lmax):
    r = (k-1.0) / (lmax-lmin)
    rt = (m-1.0) / (max(lmax, dmax) - min(lmin, dmin))
    return 2 - max(r / rt, rt / r)


def _density_max(k, m):
    return 2 - (k-1.0) / (m-1.0) if k >= m else 1.


def _simplicity(q, Q, j, lmin, lmax, lstep):
    eps = 1e-10
    n = len(Q)
    i = Q.index(q) + 1
    if ((lmin % lstep) < eps or
            (lstep - lmin % lstep) < eps) and lmin <= 0 and lmax >= 0:
        v = 1
    else:
        v = 0
    return (n - i) / (n - 1.0) + v - j


def _simplicity_max(q, Q, j):
    n = len(Q)
    i = Q.index(q) + 1
    return (n - i)/(n - 1.0) + 1. - j


def _get_ticks_talbot(dmin, dmax, n_inches, density=1.):
    # density * size gives target number of intervals,
    # density * size + 1 gives target number of tick marks,
    # the density function converts this back to a density in data units
    # (not inches)
    n_inches = max(n_inches, 2.0)  # Set minimum otherwise code can crash :(

    if dmin == dmax:
        return np.array([dmin, dmax])

    m = density * n_inches + 1.0
    only_inside = False  # we cull values outside ourselves
    Q = [1, 5, 2, 2.5, 4, 3]
    w = [0.25, 0.2, 0.5, 0.05]
    best_score = -2.0
    best = None

    j = 1.0
    n_max = 1000
    while j < n_max:
        for q in Q:
            sm = _simplicity_max(q, Q, j)

            if w[0] * sm + w[1] + w[2] + w[3] < best_score:
                j = n_max
                break

            k = 2.0
            while k < n_max:
                dm = _density_max(k, n_inches)

                if w[0] * sm + w[1] + w[2] * dm + w[3] < best_score:
                    break

                delta = (dmax-dmin)/(k+1.0)/j/q
                z = np.ceil(np.log10(delta))

                while z < float('infinity'):
                    step = j * q * 10 ** z
                    cm = _coverage_max(dmin, dmax, step*(k-1.0))

                    if (w[0] * sm +
                            w[1] * cm +
                            w[2] * dm +
                            w[3] < best_score):
                        break

                    min_start = np.floor(dmax/step)*j - (k-1.0)*j
                    max_start = np.ceil(dmin/step)*j

                    if min_start > max_start:
                        z = z+1
                        break

                    for start in range(int(min_start), int(max_start)+1):
                        lmin = start * (step/j)
                        lmax = lmin + step*(k-1.0)
                        lstep = step

                        s = _simplicity(q, Q, j, lmin, lmax, lstep)
                        c = _coverage(dmin, dmax, lmin, lmax)
                        d = _density(k, m, dmin, dmax, lmin, lmax)
                        leg = 1.  # _legibility(lmin, lmax, lstep)

                        score = w[0] * s + w[1] * c + w[2] * d + w[3] * leg

                        if (score > best_score and
                                (not only_inside or (lmin >= dmin and
                                                     lmax <= dmax))):
                            best_score = score
                            best = (lmin, lmax, lstep, q, k)
                    z += 1
                k += 1
            if k == n_max:
                raise RuntimeError('could not converge on ticks')
        j += 1
    if j == n_max:
        raise RuntimeError('could not converge on ticks')

    if best is None:
        raise RuntimeError('could not converge on ticks')
    return np.arange(best[4]) * best[2] + best[0]
