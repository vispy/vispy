# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division  # just to be safe...

import numpy as np

from .color_array import ColorArray
from .color_space import _rgb_to_hex


###############################################################################
# Color maps


# Utility functions for interpolation in NumPy.
def _vector_or_scalar(x, type='row'):
    """Convert an object to either a scalar or a row or column vector."""
    if isinstance(x, (list, tuple)):
        x = np.array(x)
    if isinstance(x, np.ndarray):
        assert x.ndim == 1
        if type == 'column':
            x = x[:, None]
    return x


def _vector(x, type='row'):
    """Convert an object to a row or column vector."""
    if isinstance(x, (list, tuple)):
        x = np.array(x, dtype=np.float32)
    elif not isinstance(x, np.ndarray):
        x = np.array([x], dtype=np.float32)
    assert x.ndim == 1
    if type == 'column':
        x = x[:, None]
    return x


def _find_controls(x, controls=None, clip=None):
    x_controls = np.clip(np.searchsorted(controls, x) - 1, 0, clip)
    return x_controls.astype(np.int32)


# Interpolation functions in NumPy.
def _mix_simple(a, b, x):
    """Mix b (with proportion x) with a."""
    x = np.clip(x, 0.0, 1.0)
    return (1.0 - x)*a + x*b


def _smoothstep_simple(a, b, x):
    y = x * x * (3. - 2. * x)
    return _mix_simple(a, b, y)


def _interpolate_multi(colors, x, controls):
    x = x.ravel()
    n = len(colors)
    # For each element in x, the control index of its bin's left boundary.
    x_step = _find_controls(x, controls, n-2)
    # The length of each bin.
    controls_length = np.diff(controls).astype(np.float32)
    # Prevent division by zero error.
    controls_length[controls_length == 0.] = 1.
    # Like x, but relative to each bin.
    _to_clip = x - controls[x_step]
    _to_clip /= controls_length[x_step]
    x_rel = np.clip(_to_clip, 0., 1.)
    return (colors[x_step],
            colors[x_step + 1],
            x_rel[:, None])


def mix(colors, x, controls=None):
    a, b, x_rel = _interpolate_multi(colors, x, controls)
    return _mix_simple(a, b, x_rel)


def smoothstep(colors, x, controls=None):
    a, b, x_rel = _interpolate_multi(colors, x, controls)
    return _smoothstep_simple(a, b, x_rel)


def step(colors, x, controls=None):
    x = x.ravel()
    """Step interpolation from a set of colors. x belongs in [0, 1]."""
    assert (controls[0], controls[-1]) == (0., 1.)
    ncolors = len(colors)
    assert ncolors == len(controls) - 1
    assert ncolors >= 2
    x_step = _find_controls(x, controls, ncolors-1)
    return colors[x_step, ...]


# GLSL interpolation functions.
def _glsl_mix(controls=None):
    """Generate a GLSL template function from a given interpolation patterns
    and control points."""
    assert (controls[0], controls[-1]) == (0., 1.)
    ncolors = len(controls)
    assert ncolors >= 2
    if ncolors == 2:
        s = "    return mix($color_0, $color_1, t);\n"
    else:
        s = ""
        for i in range(ncolors-1):
            if i == 0:
                ifs = 'if (t < %.6f)' % (controls[i+1])
            elif i == (ncolors-2):
                ifs = 'else'
            else:
                ifs = 'else if (t < %.6f)' % (controls[i+1])
            s += "%s {\n    return mix($color_%d, $color_%d, t);\n} " % \
                 (ifs, i, i+1)
    return "vec4 colormap(float t) {\n%s\n}" % s


def _glsl_step(controls=None):
    assert (controls[0], controls[-1]) == (0., 1.)
    ncolors = len(controls) - 1
    assert ncolors >= 2
    s = ""
    for i in range(ncolors-1):
        if i == 0:
            ifs = 'if (t < %.6f)' % (controls[i+1])
        elif i == (ncolors-2):
            ifs = 'else'
        else:
            ifs = 'else if (t < %.6f)' % (controls[i+1])
        s += """%s {\n    return $color_%d;\n} """ % (ifs, i)
    return """vec4 colormap(float t) {\n%s\n}""" % s


# Mini GLSL template system for colors.
def _process_glsl_template(template, colors):
    """Replace $color_i by color #i in the GLSL template."""
    for i in range(len(colors)):
        color = colors[i]
        assert len(color) == 4
        vec4_color = 'vec4(%.3f, %.3f, %.3f, %.3f)' % tuple(color)
        template = template.replace('$color_%d' % i, vec4_color)
    return template


class Colormap(object):
    """Class representing a colormap:

        t \in [0, 1] --> rgba_color

    Must be overriden. Child classes need to implement:

    colors : list of lists, tuples, or ndarrays
        The control colors used by the colormap (shape = (ncolors, 4)).
    glsl_map : string
        The GLSL function for the colormap. Use $color_0 to refer
        to the first color in `colors`, and so on. These are vec4 vectors.
    map(item) : function
        Takes a (N, 1) vector of values in [0, 1], and returns a rgba array
        of size (N, 4).

    """

    # Control colors used by the colormap.
    colors = None

    # GLSL string with a function implementing the color map.
    glsl_map = None

    def __init__(self, colors=None):
        # Ensure the colors are arrays.
        if colors is not None:
            self.colors = colors
        if not isinstance(self.colors, ColorArray):
            self.colors = ColorArray(self.colors)
        # Process the GLSL map function by replacing $color_i by the
        if len(self.colors) > 0:
            self.glsl_map = _process_glsl_template(self.glsl_map,
                                                   self.colors.rgba)

    def map(self, item):
        """Return a rgba array for the requested items.

        This function must be overriden by child classes.

        This function doesn't need to implement argument checking on `item`.
        It can always assume that `item` is a (N, 1) array of values between
        0 and 1.

        Parameters
        ----------
        item : ndarray
            An array of values in [0,1]. Expected to be a column vector.

        Returns
        -------
        rgba : ndarray
            A (N, 4) array with rgba values, where N is `len(item)`.

        """
        raise NotImplementedError()

    def __getitem__(self, item):
        if isinstance(item, tuple):
            raise ValueError('ColorArray indexing is only allowed along '
                             'the first dimension.')
        # Ensure item is either a scalar or a column vector.
        item = _vector(item, type='column')
        colors = self.map(item)
        return ColorArray(colors)

    def __setitem__(self, item, value):
        raise RuntimeError("It is not possible to set items to "
                           "Colormap instances.")

    def _repr_html_(self):
        n = 500
        html = ("""
                <table style="width: 500px;
                              height: 50px;
                              border: 0;
                              margin: 0;
                              padding: 0;">
                """ +
                '\n'.join([(('<td style="background-color: %s; border: 0; '
                             'width: 1px; margin: 0; padding: 0;"></td>') %
                            _rgb_to_hex(color)[0])
                           for color in self[np.linspace(0., 1., n)].rgb]) +
                """
                </table>
                """)
        return html


def _default_controls(ncolors):
    """Generate linearly spaced control points from a set of colors."""
    return np.linspace(0., 1., ncolors)


class LinearGradient(Colormap):
    """A linear gradient with an arbitrary number of colors and control
    points in [0,1]."""
    def __init__(self, colors, controls=None):
        # Default controls.
        if controls is None:
            controls = _default_controls(len(colors))
        assert len(controls) == len(colors)
        self.controls = np.array(controls, dtype=np.float32)
        # Generate the GLSL map.
        self.glsl_map = _glsl_mix(controls)
        super(LinearGradient, self).__init__(colors)

    def map(self, x):
        return mix(self.colors.rgba, x, self.controls)


class DiscreteColormap(Colormap):
    """A discrete colormap with an arbitrary number of colors and control
    points in [0,1]."""
    def __init__(self, colors, controls=None):
        # Default controls.
        if controls is None:
            controls = _default_controls(len(colors) + 1)
        assert len(controls) == len(colors) + 1
        self.controls = np.array(controls, dtype=np.float32)
        # Generate the GLSL map.
        self.glsl_map = _glsl_step(self.controls)
        super(DiscreteColormap, self).__init__(colors)

    def map(self, x):
        return step(self.colors.rgba, x, self.controls)


class Fire(Colormap):
    colors = [(1.0, 1.0, 1.0, 1.0),
              (1.0, 1.0, 0.0, 1.0),
              (1.0, 0.0, 0.0, 1.0)]

    glsl_map = """
    vec4 fire(float t) {
        return mix(mix($color_0, $color_1, t),
                   mix($color_1, $color_2, t*t), t);
    }
    """

    def map(self, t):
        a, b, d = self.colors.rgba
        c = _mix_simple(a, b, t)
        e = _mix_simple(b, d, t**2)
        return _mix_simple(c, e, t)


class Grays(Colormap):
    glsl_map = """
    vec4 grays(float t) {
        return vec4(t, t, t, 1.0);
    }
    """

    def map(self, t):
        if isinstance(t, np.ndarray):
            return np.hstack([t, t, t, np.ones(t.shape)]).astype(np.float32)
        else:
            return np.array([t, t, t, 1.0], dtype=np.float32)


class Ice(Colormap):
    glsl_map = """
    vec4 ice(float t) {
        return vec4(t, t, 1.0, 1.0);
    }
    """

    def map(self, t):
        if isinstance(t, np.ndarray):
            return np.hstack([t, t, np.ones(t.shape),
                              np.ones(t.shape)]).astype(np.float32)
        else:
            return np.array([t, t, 1.0, 1.0], dtype=np.float32)


class Hot(Colormap):
    colors = [(0., .33, .66, 1.0),
              (.33, .66, 1., 1.0)]

    glsl_map = """
    vec4 hot(float t) {
        return vec4(smoothstep($color_0.rgb, $color_1.rgb, vec3(t, t, t)),
                    1.0);
    }
    """

    def map(self, t):
        n = len(self.colors)
        return np.hstack((_smoothstep_simple(self.colors.rgba[0, :3],
                                             self.colors.rgba[1, :3],
                                             t),
                         np.ones((n, 1))))


class Winter(Colormap):
    colors = [(0.0, 0.0, 1.0, 1.0),
              (0.0, 1.0, 0.5, 1.0)]

    glsl_map = """
    vec4 winter(float t) {
        return mix($color_0, $color_1, sqrt(t));
    }
    """

    def map(self, t):
        return _mix_simple(self.colors.rgba[0],
                           self.colors.rgba[1],
                           np.sqrt(t))


_colormaps = dict(
    autumn=LinearGradient([(1., 0., 0., 1.), (1., 1., 0., 1.)]),
    blues=LinearGradient([(1., 1., 1., 1.), (0., 0., 1., 1.)]),
    cool=LinearGradient([(0., 1., 1., 1.), (1., 0., 1., 1.)]),
    greens=LinearGradient([(1., 1., 1., 1.), (0., 1., 0., 1.)]),
    reds=LinearGradient([(1., 1., 1., 1.), (1., 0., 0., 1.)]),
    spring=LinearGradient([(1., 0., 1., 1.), (1., 1., 0., 1.)]),
    summer=LinearGradient([(0., .5, .4, 1.), (1., 1., .4, 1.)]),
    fire=Fire(),
    grays=Grays(),
    hot=Hot(),
    ice=Ice(),
    winter=Winter(),
)


def get_colormap(name):
    """Return a Colormap instance given its name."""
    return _colormaps[name]


def get_colormaps():
    """Return the list of colormap names."""
    return list(sorted(_colormaps.keys()))
