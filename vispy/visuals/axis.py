# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from cgi import test
import datetime
from datetime import date
from email.utils import parsedate_to_datetime
from select import select
from dateutil.relativedelta import relativedelta, MO
from datetime import timedelta
import math
import time

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
    axis_label_max_width : int
        Max char length a axis label can have before string will be split in multiple
        rows with max axis_label_max_width chars per row
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
    axis_mapping : array-like
        Axis mapping maps an arbitrary array-like object of type numpy array of numpy.datetime64 or
        list of datetime dates, for better performance use list since numpy will be converted to list anyway
        All other types will be converted to strings
        In case of string mapping the array/list will only be applied to integers
        (0, 1, 2, 3, 4, 5, etc) not (0.5, 0.666, 0.75, 1.5, etc.) floats won't be displayed,
        this is not the case if you provide a array of datetime64 or list of datetime dates
    interpolation_between_dates : bool
        This generates new dates between two dates mapped to the axis 
    interpolation_to_infinity : bool
        Extends axis mapping along the hole axis even if the mapping has run out of dates (only linear time)
    date_format_string : string
        This string allows you to control the format of the time labels i.e. %m/%d/%Y, %H:%M:%S
        axis_mapping has to be used, if not this does nothing
        lookup datetime.date.strftime
    date_verbose : bool
        If True underneath the time labels it shows the mapped integer
        axis_mapping has to be used, if not this does nothing
    disable_warning : bool
        If True disables warning that axis mapping ran out of entries
    rounding_seconds : bool
        Controls if datetime seconds get rounded
        axis_mapping has to be used, if not this does nothing
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
                 axis_label_max_width=20,
                 axis_font_size=10,
                 font_size=None,
                 anchors=None,
                 axis_mapping=None,
                 interpolation_between_dates=True,
                 interpolation_to_infinity=True,
                 date_format_string=None,
                 date_verbose=True,
                 disable_warning=False,
                 rounding_seconds=False):

        if scale_type != 'linear':
            raise NotImplementedError('only linear scaling is currently '
                                      'supported')

        if font_size is not None:
            tick_font_size = font_size
            axis_font_size = font_size

        self._pos = None
        self._domain = None

        self.axis_mapping_is_date = False

        self.axis_mapping = axis_mapping
        self._apply_axis_mapping()

        self.interpolation_between_dates = interpolation_between_dates
        self.interpolation_to_infinity = interpolation_to_infinity

        self.date_format_string = date_format_string
        self.rounding_seconds = rounding_seconds
        self.date_verbose = date_verbose

        self.disable_warning = disable_warning

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
        self.axis_label_max_width = axis_label_max_width

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

    def update_axis_mapping(self, new_mapping):
        self.axis_mapping = new_mapping
        self._apply_axis_mapping()
        self._update_subvisuals()

    def _apply_axis_mapping(self):
        if self.axis_mapping is not None:
            if isinstance(self.axis_mapping, np.ndarray):
                self._axis_mapping_instance_checking(np.ndarray)
            elif isinstance(self.axis_mapping, list):
                self._axis_mapping_instance_checking(list)
            elif isinstance(self.axis_mapping, tuple):
                self._axis_mapping_instance_checking(tuple)

    def _axis_mapping_instance_checking(self, checking_list_type):
        if self.axis_mapping is not None:
            if isinstance(self.axis_mapping, np.ndarray):
                if len(self.axis_mapping.shape) == 1:
                    self.axis_mapping = self.axis_mapping.reshape(self.axis_mapping.shape[0], 1)

                elif len(self.axis_mapping.shape) == 2:
                    if self.axis_mapping.shape[1] != 1:
                        raise ValueError('axis_mapping should only have one column')

                else:
                    raise ValueError('3d is not expected, just 2d')

                if np.issubdtype(self.axis_mapping[0][0].dtype, np.datetime64):
                    self.axis_mapping = _date_to_datetime_converter(
                        [list(x)[0].astype(datetime.datetime) for x in self.axis_mapping])
                    self.axis_mapping_is_date = True

                elif np.issubdtype(self.axis_mapping[0][0].dtype, datetime.datetime):
                    self.axis_mapping = _date_to_datetime_converter(
                        [list(x)[0].astype(datetime.datetime) for x in self.axis_mapping])
                    self.axis_mapping_is_date = True

                elif np.issubdtype(self.axis_mapping[0][0].dtype, datetime.date):
                    self.axis_mapping = _date_to_datetime_converter(
                        [datetime.datetime.combine(list(x)[0], datetime.time.min) for x in self.axis_mapping])
                    self.axis_mapping_is_date = True

                else:
                    self.axis_mapping = [str(list(x)[0]) for x in self.axis_mapping]

            else:
                if isinstance(self.axis_mapping, checking_list_type):
                    if isinstance(self.axis_mapping[0], np.datetime64):
                        self.axis_mapping = _date_to_datetime_converter(
                            [x.astype(datetime.datetime) for x in self.axis_mapping])
                        self.axis_mapping_is_date = True

                    elif isinstance(self.axis_mapping[0], datetime.datetime):
                        self.axis_mapping = _date_to_datetime_converter(self.axis_mapping)
                        self.axis_mapping_is_date = True

                    elif isinstance(self.axis_mapping[0], datetime.date):
                        self.axis_mapping = _date_to_datetime_converter(
                            [datetime.datetime.combine(x, datetime.time.min) for x in self.axis_mapping])
                        self.axis_mapping_is_date = True

                    elif isinstance(self.axis_mapping[0], list):
                        if isinstance(self.axis_mapping[0][0], datetime.datetime):
                            self.axis_mapping = _date_to_datetime_converter([x[0] for x in self.axis_mapping])
                            self.axis_mapping_is_date = True

                        if isinstance(self.axis_mapping[0][0], datetime.date):
                            self.axis_mapping = _date_to_datetime_converter(
                                [datetime.datetime.combine(x[0], datetime.time.min) for x in
                                 self.axis_mapping])
                            self.axis_mapping_is_date = True

                        elif isinstance(self.axis_mapping[0][0], np.datetime64):
                            self.axis_mapping = _date_to_datetime_converter(
                                [x[0].astype(datetime.datetime) for x in self.axis_mapping])
                            self.axis_mapping_is_date = True

                        else:
                            self.axis_mapping = [x[0] for x in self.axis_mapping]

                    else:
                        if checking_list_type == tuple:
                            ValueError('Tuple is only supported with date interpolation, so only a tuple of datetime ')
                        else:
                            self.axis_mapping = None
                            self.axis_mapping_is_date = False
                            ValueError('Could not parse axis mapping')

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
        return math.degrees(math.atan2(y2 - y1, x2 - x1))

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
            self._get_tick_frac_labels(1 if self.axis.axis_mapping is not None else 2)

        # print(f'tick_labels: {tick_labels}')

        tick_labels = np.array([" " if x == '' else x for x in tick_labels], dtype=str)

        tick_labels = np.char.replace(tick_labels, " ", "\n")

        try:
            string_width = np.char.str_len([max(x, key=len) if x != '' else ' ' for x
                                        in np.char.splitlines(tick_labels)])

        except Exception as e:
            print(e)
            exit(0)

        

        b = np.where(string_width <= self.axis.axis_label_max_width, 0, string_width)

        for i, j in enumerate(b):
            if j != 0:
                for k in range(int(j / self.axis.axis_label_max_width)):
                    tick_labels[i] = tick_labels[i][:self.axis.axis_label_max_width * (k + 1)] + "\n" + \
                        tick_labels[i][self.axis.axis_label_max_width * (k + 1):]

        string_line_count = np.char.count(tick_labels, '\n')

        tick_pos, tick_label_pos, axis_label_pos, anchors = \
            self._get_tick_positions(major_tick_fractions,
                                     minor_tick_fractions, string_line_count)
        return tick_pos, tick_labels, tick_label_pos, anchors, axis_label_pos

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions, string_line_count):
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

        orientation = np.all(major_origins == major_origins[0, :], axis=0)

        line_count = string_line_count.reshape((string_line_count.shape[0], 1)) + 1

        vertical_offset = np.column_stack((line_count, line_count))

        if orientation[1]:
            vertical_offset[vertical_offset < 1] = 1
            adj = vertical_offset * orientation * label_vector
        else:
            adj = orientation * label_vector

        # print(f'adj shape: {adj.shape}')

        # print(f'major_origins shape: {major_origins.shape}')	

        # if adj.shape != major_origins.shape:
        #     print(f'shape mismatch: {adj.shape} != {major_origins.shape}')
        #     print(f'adj: {adj}')
        #     print(f'major_origins: {major_origins}')

        tick_label_pos = None

        print(f'major_origins: {major_origins.shape} adj: {adj.shape}')

        if adj.shape != major_origins.shape:
            print(f'major_origins: {major_origins[0:-1]} major_origins.shape: {major_origins.shape}, major_origins.shape: {major_origins[0:-1].shape}')
            if len(major_origins.shape) == len(adj.shape):
                print(f'adj: {adj.shape} major_origins {major_origins.shape} \n\n\n\n\n')
                if major_origins.shape[0] - adj.shape[0] > 0:
                    print(f'major_origins[0:{-(major_origins.shape[0] - adj.shape[0])}]')
                    major_origins = major_origins[0: -(major_origins.shape[0] - adj.shape[0])] # wrong! adj: (9, 2) major_origins (10, 2)
                    tick_label_pos = major_origins + adj
                    print('if\n\n\n')
                elif len(major_origins[0]) - len(adj[0]) < 0:
                    adj = adj[0: -(adj.shape[0] - major_origins.shape[0] + 1), adj.shape[1]]
                    tick_label_pos = major_origins + adj
                    print('elif\n\n\n')
            else:
                tick_label_pos = major_origins + adj
                print('else\n\n\n')
        else:
            tick_label_pos = major_origins + adj

        # if major_origins.shape[0] != adj[0]:
        #     if len(major_origins[0]) - len(adj[0]) > 0:
        #         major_origins = major_origins[0: -(len(major_origins[0]) - len(adj[0]) + 1), len(major_origins[1])]
        #         tick_label_pos = major_origins + adj
        #         print('if\n\n\n')

        #     elif len(major_origins[0]) - len(adj[0]) < 0:
        #         adj = adj[0: -(len(adj[0]) - len(major_origins[0]) + 1), len(adj[1])]
        #         tick_label_pos = major_origins + adj
        #         print('elif\n\n\n')

        # else:
        #     tick_label_pos = major_origins + adj

        # tick_label_pos = major_origins + adj
        

        axis_label_pos = 0.5 * (self.axis.pos[0] +
                                self.axis.pos[1]) + axislabel_vector

        num_major = len(major_tick_fractions)
        num_minor = len(minor_tick_fractions)

        c = np.empty([(num_major + num_minor) * 2, 2])

        c[0:(num_major - 1) * 2 + 1:2] = major_origins
        c[1:(num_major - 1) * 2 + 2:2] = major_endpoints
        c[(num_major - 1) * 2 + 2::2] = minor_origins
        c[(num_major - 1) * 2 + 3::2] = minor_endpoints

        return c, tick_label_pos, axis_label_pos, anchors

    def _tile_ticks(self, frac, tickvec):
        """Tiles tick marks along the axis."""
        origins = np.tile(self.axis._vec, (len(frac), 1))
        origins = self.axis.pos[0].T + (origins.T * frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self, density=2):
        """Get the major ticks, minor ticks, and major labels"""
        minor_num = 4  # number of minor ticks per major division
        if self.axis.scale_type == 'linear':
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

            if self.axis.axis_mapping_is_date and self.axis.interpolation_to_infinity:
                last_date = self.axis.axis_mapping[len(self.axis.axis_mapping) - 1]
                second_to_last_date = self.axis.axis_mapping[len(self.axis.axis_mapping) - 2]
                date_integer_delta = last_date - second_to_last_date
                
                for j in range((int(domain[1]) + 1) - (len(self.axis.axis_mapping) - 1)):
                    self.axis.axis_mapping.append(last_date + ((j + 1) * date_integer_delta))
                # print(f'domain: {domain}, axis_mapping: {len(self.axis.axis_mapping)}')
                # print(f'axis_mapping: {len(self.axis.axis_mapping)}')

            major, datecode, datestring = _get_ticks_talbot(domain[0], domain[1], n_inches, density, mapping=self.axis.axis_mapping)

            # if self.axis.axis_mapping is not None:
            #     # print(f'domain: {domain}, n_inches: {n_inches}')

            #     # print(f'major: {major}')

            #     print(f'major_date: {_get_ticks_talbot_dates(domain[0], domain[1], self.axis.axis_mapping, density)}')

            #     pass

            labels = []
            if self.axis.axis_mapping is not None:
                # print(f'major: {major}, type: {type(major)}, len: {len(major)}, major first: {major[0]}, firsttype: {type(major[0])}')


                # for i in major:
                #     try:
                #         print(f'i: {i}, self.axis.axis_mapping: {self.axis.axis_mapping[int(i)]}')
                #     except IndexError:
                #         print(f'IndexError i: {i}, self.axis.axis_mapping: {len(self.axis.axis_mapping)}')
                for x in major:
                    if x > domain[1]:
                        break
                    
                    label_string = ''
                    if x >= 0:
                        # try:
                        # print(f'dmax: {int(domain[1])}, len(axis_mapping): {len(self.axis.axis_mapping)}, x: {x}')

                        label = self.axis.axis_mapping[int(x)]
                        label_plus_one = self.axis.axis_mapping[int(x) + 1]
                        # except IndexError:
                            # label = x
                            # label_plus_one = None
                            # if self.axis.axis_mapping_is_date and self.axis.interpolation_to_infinity:
                            #     last_date = self.axis.axis_mapping[len(self.axis.axis_mapping) - 1]
                            #     second_to_last_date = self.axis.axis_mapping[len(self.axis.axis_mapping) - 2]
                            #     date_integer_delta = last_date - second_to_last_date
                            #     for j in range((int(x) + 1) - (len(self.axis.axis_mapping) - 1)):
                            #         self.axis.axis_mapping.append(last_date + ((j + 1) * date_integer_delta))
                                # disable_warning = True
                                # label = self.axis.axis_mapping[int(x)]
                                # label_plus_one = self.axis.axis_mapping[int(x) + 1]
                                # disable_warning = True
                                # print(f'dmax: {int(domain[1])}, len(axis_mapping): {len(self.axis.axis_mapping)}')
                                # label = self.axis.axis_mapping[int(dmax)]
                                # label_plus_one = self.axis.axis_mapping[int(dmax) + 1]
                        # if not (disable_warning or self.axis.disable_warning):
                        #     warnings.warn("Axis mapping ran out of data at index " + str(int(x)) +
                        #                     " use update_axis_mapping() in AxisVisual to extend the mapping range in "
                        #                     "Runtime or map a longer list/array in the first place - As last resort "
                        #                     "you can disable this warning by setting disable_warning to True")
                        # if not self.axis.disable_warning:
                        #     label = x
                        # if x.is_integer():
                        
                        # if np.all(np.mod(x, 1) == 0):

                        if isinstance(x, int):
                            # print(f'int x: {x}')
                            # x = x.astype(int)
                            # label_string = str(self.axis.axis_mapping[int(x)])
                            label_string = _label_string_for_datetime(x, label, self.axis.date_format_string,
                                                                      self.axis.date_verbose)
                        else:
                            # print(f'float x: {x}')
                            if isinstance(label, datetime.datetime) and label_plus_one is not None and self.axis.interpolation_between_dates:
                                a = label
                                b = label_plus_one
                                # print(f'x: {x}')
                                date = (b - (b - a) / (1 - (x - int(x))) ** -1)  # here the magic of date interpolation happens
                                # print(f'date: {date} a: {a}, b: {b}, x: {x}, int x: {int(x)}')
                                label_string = _label_string_for_datetime(x, date, self.axis.date_format_string,
                                                                            self.axis.date_verbose)
                    labels.append(label_string)
                
            else:
                labels = ['%g' % x for x in major]

            # print(f'labels1: {labels}')

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
        # print(f'labels: {labels}\n\n\n')
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
    if dv == 0:  # maxabsv == 0 is a special case of this.
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
    r = (k - 1.0) / (lmax - lmin)
    rt = (m - 1.0) / (max(lmax, dmax) - min(lmin, dmin))
    return 2 - max(r / rt, rt / r)


def _density_max(k, m):
    return 2 - (k - 1.0) / (m - 1.0) if k >= m else 1.


def _simplicity(q, Q, j, lmin, lmax, lstep):
    eps = 1e-10
    n = len(Q)
    i = Q.index(q) + 1
    if ((lmin % lstep) < eps or (lstep - lmin % lstep) < eps) and lmin <= 0 and lmax >= 0:
        v = 1
    else:
        v = 0
    return (n - i) / (n - 1.0) + v - j


def _simplicity_max(q, Q, j):
    n = len(Q)
    i = Q.index(q) + 1
    return (n - i) / (n - 1.0) + 1. - j

def _negative_equals_zero(a):
    return (abs(a)+a)/2 

def _fp_to_date(first_axis_mapping, second_axis_mapping, fp):
    return (second_axis_mapping - (second_axis_mapping - first_axis_mapping) / (1 - (fp - int(fp))) ** -1)


def _get_ticks_talbot(dmin, dmax, n_inches, density=2., mapping=None):
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

                delta = (dmax - dmin) / (k + 1.0) / j / q
                z = np.ceil(np.log10(delta))

                while z < float('infinity'):
                    step = j * q * 10 ** z
                    cm = _coverage_max(dmin, dmax, step * (k - 1.0))

                    if (w[0] * sm +
                            w[1] * cm +
                            w[2] * dm +
                            w[3] < best_score):
                        break

                    min_start = np.floor(dmax / step) * j - (k - 1.0) * j
                    max_start = np.ceil(dmin / step) * j

                    if min_start > max_start:
                        z = z + 1
                        break

                    for start in range(int(min_start), int(max_start) + 1):
                        lmin = start * (step / j)
                        lmax = lmin + step * (k - 1.0)
                        lstep = step

                        s = _simplicity(q, Q, j, lmin, lmax, lstep)
                        c = _coverage(dmin, dmax, lmin, lmax)
                        d = _density(k, m, dmin, dmax, lmin, lmax)
                        leg = 1.  # _legibility(lmin, lmax, lstep)

                        score = w[0] * s + w[1] * c + w[2] * d + w[3] * leg
                        # print(f'k: {k}, q: {q}')
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


    if mapping:
        
        absolut_distance = abs(dmax) - dmin
        print(f'test distance: {absolut_distance}')
        tick_amount = best[4]
        if dmin < 0:
            dmin = 0
            tick_amount = int(abs(dmax) / absolut_distance * tick_amount) + 1
        if dmax < 0:
            dmax = 0
        else:
            print(f'tock_amount: {best[4]},  tick_amount: {tick_amount}')

            first_axis_mapping = mapping[int(dmin)]
            second_axis_mapping = mapping[int(dmin) + 1]

            sec = [[0.000001*3, relativedelta(microseconds=+1), 'ms', 1], [0.000002*3, relativedelta(microseconds=+2), 'ms', 2], [0.000005*3, relativedelta(microseconds=+5), 'ms', 5],
                 [0.00001*3, relativedelta(microseconds=+10), 'ms', 10], [0.00002*3, relativedelta(microseconds=+20), 'ms', 20], [0.00005*3, relativedelta(microseconds=+50), 'ms', 50], 
                 [0.0001*3, relativedelta(microseconds=+100), 'ms', 100], [0.0002*3, relativedelta(microseconds=+200), 'ms', 200], [0.0005*3, relativedelta(microseconds=+500), 'ms', 500], 
                 [0.001*3, relativedelta(microseconds=+1_000), 'ms', 1_000], [0.002*3, relativedelta(microseconds=+2_000), 'ms', 2_000], [0.005*3, relativedelta(microseconds=+5_000), 'ms', 5_000], 
                 [0.01*3, relativedelta(microseconds=+10_000), 'ms', 10_000], [0.02*3, relativedelta(microseconds=+20_000), 'ms', 20_000], [0.05*3, relativedelta(microseconds=+50_000), 'ms', 50_000], 
                 [0.1*3, relativedelta(microseconds=+100_000), 'ms', 100_000], [0.2*3, relativedelta(microseconds=+200_000), 'ms', 200_000], [0.5*3, relativedelta(microseconds=+500_000), 'ms', 500_000],
                 
                 [3*1, relativedelta(seconds=+1), 's', 1], 
                 
                 [3*2, relativedelta(seconds=+2), 's', 2], [3*5, relativedelta(seconds=+5), 's', 5], 
                 [3*10, relativedelta(seconds=+10), 's', 10], [3*15, relativedelta(seconds=+15), 's', 15], 
                 [3*30, relativedelta(seconds=+30), 's', 30], 
                 
                 [2*60, relativedelta(minutes=+1), 'm', 1], 
                 
                 [4*120, relativedelta(minutes=+2), 'm', 2], [2*300, relativedelta(minutes=+5), 'm', 5], 
                 [3*600, relativedelta(minutes=+10), 'm', 10], [3*900, relativedelta(minutes=+15), 'm', 15], 
                 [2*1200, relativedelta(minutes=+20), 'm', 20], [3*1800, relativedelta(minutes=+30), 'm', 30], 
                 
                 [3*3600, relativedelta(hours=+1), 'h', 1], 
                 
                 [3*7200, relativedelta(hours=+2), 'h', 2], 
                 [3*10800, relativedelta(hours=+3), 'h', 3], [3*14400, relativedelta(hours=+4), 'h', 4], 
                 [3*21600, relativedelta(hours=+6), 'h', 6], [3*28800, relativedelta(hours=+8), 'h', 8], 
                 [3*43200, relativedelta(hours=+12), 'h', 12], 
                 
                 [3*86400, relativedelta(days=+1), 'd', 1], 
                 
                 [6*86400, relativedelta(days=+2), 'd', 2], [9*86400, relativedelta(days=+3), 'd', 3],  [15 * 86400, relativedelta(days=+5), 'd', 5],
                 
                 [21*86400, relativedelta(weeks=+1), 'W', 1], 
                 [3*14*86400, relativedelta(weeks=+2), 'W', 2], 

                 [93*86400, relativedelta(months=+1), 'M', 1], 

                 [3*2*31*86400, relativedelta(months=+2), 'M', 2], [3*3*31*86400, relativedelta(months=+3), 'M', 3], 
                 [3*4*31*86400, relativedelta(months=+4), 'M', 4], [3*6*31*86400, relativedelta(months=+6), 'M', 6],  
                 
                 [4*365*86400, relativedelta(years=+1), 'Y', 1],
                 
                 [4*2*365*86400, relativedelta(years=+2), 'Y', 2], [4*3*365*86400, relativedelta(years=+3), 'Y', 3], [4*5*365*86400, relativedelta(years=+5), 'Y', 5],
                 [4*10*365*86400, relativedelta(years=+10), 'Y', 10], [4*25*365*86400, relativedelta(years=+25), 'Y', 25], [4*50*365*86400, relativedelta(years=+50), 'Y', 50],
                 [4*100*365*86400, relativedelta(years=+1), 'Y', 100]]
            
            seconds_between_axis_mapping = (second_axis_mapping-first_axis_mapping).total_seconds()

            delta = best[4] * (second_axis_mapping-first_axis_mapping).total_seconds()

            delta = absolut_distance * (second_axis_mapping-first_axis_mapping).total_seconds() / best[4] * 4

            closest_min = sec[min(range(len(sec)), key = lambda i: abs(sec[i][0]-delta))]

            print(f'secounds: {seconds_between_axis_mapping}, delta: {delta}, closest_min: {closest_min}')

            step_distance = closest_min[0] / seconds_between_axis_mapping
            
            step = int((dmax - dmin) / step_distance) + 2

            DMIN = None

            a = mapping[int(dmin)]
            b = mapping[int(dmin) + 1]

            multiplier = 1
            
            print(f'best: {best}')
            if closest_min[2] == 'ms':

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                print(f'dmin: {dmin}, pydate_at_dmin: {pydate_at_dmin}')

                date_calculated_first_tick_current_view = pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(microseconds=int(closest_min[1].microseconds)))
                
                # print(f'\n\n')

                # print(f'date_calculated_first_tick_current_view: {date_calculated_first_tick_current_view}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view


            elif closest_min[2] == 's':

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                print(f'dmin: {dmin}, pydate_at_dmin: {pydate_at_dmin}')

                date_calculated_first_tick_current_view = pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(seconds=int(closest_min[1].seconds)))
                
                # print(f'\n\n')

                # print(f'date_calculated_first_tick_current_view: {date_calculated_first_tick_current_view}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view


            elif closest_min[2] == 'm':

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                print(f'dmin: {dmin}, pydate_at_dmin: {pydate_at_dmin}')

                date_calculated_first_tick_current_view = pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(minutes=int(closest_min[1].minutes)))
                
                # print(f'\n\n')

                # print(f'date_calculated_first_tick_current_view: {date_calculated_first_tick_current_view}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view
                

            elif closest_min[2] == 'h':

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                date_calculated_first_tick_current_view = pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(hours=int(closest_min[1].hours)))
                
                print(f'\n\n')

                print(f'date_calculated_first_tick_current_view: {date_calculated_first_tick_current_view}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view

            elif closest_min[2] == 'd':

                print(f'\n\n')

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()
                
                date_calculated_first_tick_current_view = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1))) + timedelta( (pydate_at_dmin.day % closest_min[1].days))
                

                print(f'pydate_at_dmin: {pydate_at_dmin}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view

                print(f'\n\n')

            elif closest_min[2] == 'W':

                print(f'\n\n')

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()
                
                date_calculated_first_tick_current_view = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1))) + relativedelta(weekday=MO, hour=0, minute=0, second=0, microsecond=0)

                print(f'pydate_at_dmin: {pydate_at_dmin}')

                print(f'date_calculated_first_tick_current_view: {date_calculated_first_tick_current_view}')

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'd reverse calc: {(b - (b - a) / (1 - (dmin - int(dmin))) ** -1)}')

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view

                print(f'\n\n')

                
            elif closest_min[2] == 'M':

                print(f'\n\n')

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                pydate_day_at_dmin = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1)))

                potential_first_mounths = []

                for i in range(int(12 / closest_min[3]) + 1):
                    if (1 + closest_min[3] * i) > 12:
                        test1 = datetime.datetime(pydate_day_at_dmin.year + 1, ((1 + closest_min[3] * i) - 12), 1)
                    else:
                        test1 = datetime.datetime(pydate_day_at_dmin.year, ((1 + closest_min[3] * i)), 1)
                    potential_first_mounths.append(test1)

                round_date_to_full_day = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1))) 
                
                delta_days_to_potential_first_mounths = []

                for i in potential_first_mounths:
                    delta_days = (i - round_date_to_full_day).days
                    if delta_days >= 0:
                        delta_days_to_potential_first_mounths.append(delta_days) 

                date_calculated_first_tick_current_view = round_date_to_full_day + timedelta(days=min(delta_days_to_potential_first_mounths))

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view

                print(f'\n\n')


            elif closest_min[2] == 'Y':
                print(f'\n\n')

                pydate_at_dmin = (b - (b - a) / (1 - (dmin - int(dmin))) ** -1).to_pydatetime()

                pydate_day_at_dmin = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1)))

                round_date_to_full_day = (pydate_at_dmin + (datetime.datetime.min - pydate_at_dmin) % (timedelta(days=1))) 

                print(f'calc: {datetime.datetime(round_date_to_full_day.year + 1, 1, 1) - round_date_to_full_day}')

                add_days = datetime.datetime(round_date_to_full_day.year + 1, 1, 1) - round_date_to_full_day

                if add_days.days >= 365:
                    add_days = 0
                else:
                    add_days = add_days.days

                print(f'round_date_to_full_day: {round_date_to_full_day}')

                pre_date_calculated_first_tick_current_view = round_date_to_full_day + timedelta(days=add_days)

                date_calculated_first_tick_current_view = datetime.datetime(pre_date_calculated_first_tick_current_view.year - (pre_date_calculated_first_tick_current_view.year % closest_min[3]) + (closest_min[3] if add_days != 0 and closest_min[3] != 1 else 0), 1, 1)

                # fp_calculated_first_tick_current_view = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                DMIN = dmin + (date_calculated_first_tick_current_view - pydate_at_dmin).total_seconds() / seconds_between_axis_mapping

                print(f'fp to date: {_fp_to_date(a, b, dmin)}')

                deltasec = date_calculated_first_tick_current_view

                print(f'\n\n')

                

            print(f'deeltasec: {deltasec}, multiplier: {multiplier}, closest_min: {closest_min[1]}, test: {multiplier * closest_min[1]}')
            

            date_list = [deltasec + jk * multiplier * closest_min[1] for jk in range(int(tick_amount + 2))]
            return_list = []
            return_list.append(DMIN)
            for i in range(len(date_list)-1):
                # print((date_list[i+1] - date_list[0]))
                # print((b - (b - a) / (1 - (DMIN - int(DMIN))) ** -1) + (date_list[i+1] - date_list[0]))
                # print(f'a: {a}, b: {b}, DMIN: {(DMIN + ((date_list[i+1] - date_list[0]).total_seconds() / secounds))}, int dmin: {int((DMIN + ((date_list[i+1] - date_list[0]).total_seconds() / secounds)))}')

                # print(f'reverse calc: {(b - (b - a) / (1 - ((DMIN + ((date_list[i+1] - date_list[0]).total_seconds() / secounds)) - int((DMIN + ((date_list[i+1] - date_list[0]).total_seconds() / secounds))))) ** -1)}')
                return_list.append((DMIN + ((date_list[i+1] - date_list[0]).total_seconds() / seconds_between_axis_mapping)))
            #     print(f'count: {((date_list[i+1] - date_list[0]).total_seconds() / secounds)} delta: {(date_list[i+1] - date_list[i]).total_seconds() / secounds}')

            # print(f'DMIN: {DMIN}, steps: {step}, step_distance: {step_distance}, closest_sec_value: {closest_sec_value}, delta: {delta}')
            # print(f'dmin: {dmin}, dmax: {dmax}, delta1: {(best[1] - best[0])}, step: {step}')
            # print(f'best[0]: {best[0]}, best[1]: {best[1]}, best[2]: {best[2]}, best[3]: {best[3]}, best[4]: {best[4]}')
            # print(f'date_list: {date_list}')
            # print(np.arange(step, dtype=np.float64) * step_distance + DMIN)

            print(f'date_list: {date_list}')

            # print(f'return_list: {return_list}')

            # if step > 3:
            # return np.arange(step, dtype=np.float64) * step_distance + DMIN, None, None

            # if closest_sec_value == 86400:
            #     step_distance = step_distance * (int((((dmax - dmin) / (sec[-1] / secounds) + 1) / best[4])) + 1)

            print('\n\n\n')
            return return_list, None, None


    return np.arange(best[4], dtype=np.int32) * best[2] + best[0], None, None

def _label_string_for_datetime(tick_integer, axis_label, strftime_string, verbose):
    if strftime_string is not None:
        try:
            axis_label = str(axis_label.strftime(strftime_string))
            return (axis_label + " " + str(tick_integer)) if verbose else axis_label
        except AttributeError:
            print(f"axis_label {axis_label} type: {type(axis_label)}")
            return (str(tick_integer)) if verbose else ""
    else:
        return (str(axis_label) + " " + str(tick_integer)) if verbose else axis_label


def _date_to_datetime_converter(list_of_datetime):
    print("Ï'm i getting called?")
    if isinstance(list_of_datetime[0], datetime.date):
        if not isinstance(list_of_datetime[0], datetime.datetime):
            for i, j in enumerate(list_of_datetime):
                print('convert')
                list_of_datetime[i] = datetime.datetime.combine(j, datetime.time.min)
    return list_of_datetime
