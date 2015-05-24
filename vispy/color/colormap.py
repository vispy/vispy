# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division  # just to be safe...
import inspect

import numpy as np

from .color_array import ColorArray
from ..ext.six import string_types
from ..ext.cubehelix import cubehelix
from ..ext.husl import husl_to_rgb

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


# Normalization
def _normalize(x, cmin=None, cmax=None, clip=True):
    """Normalize an array from the range [cmin, cmax] to [0,1],
    with optional clipping."""
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    if cmin is None:
        cmin = x.min()
    if cmax is None:
        cmax = x.max()
    if cmin == cmax:
        return .5 * np.ones(x.shape)
    else:
        cmin, cmax = float(cmin), float(cmax)
        y = (x - cmin) * 1. / (cmax - cmin)
        if clip:
            y = np.clip(y, 0., 1.)
        return y


# Interpolation functions in NumPy.
def _mix_simple(a, b, x):
    """Mix b (with proportion x) with a."""
    x = np.clip(x, 0.0, 1.0)
    return (1.0 - x)*a + x*b


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


def smoothstep(edge0, edge1, x):
    """ performs smooth Hermite interpolation
        between 0 and 1 when edge0 < x < edge1.  """
    # Scale, bias and saturate x to 0..1 range
    x = np.clip((x - edge0)/(edge1 - edge0), 0.0, 1.0)
    # Evaluate polynomial
    return x*x*(3 - 2*x)


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
            adj_t = '(t - %s) / %s' % (controls[i],
                                       controls[i+1] - controls[i])
            s += ("%s {\n    return mix($color_%d, $color_%d, %s);\n} " %
                  (ifs, i, i+1, adj_t))
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
    for i in range(len(colors) - 1, -1, -1):
        color = colors[i]
        assert len(color) == 4
        vec4_color = 'vec4(%.3f, %.3f, %.3f, %.3f)' % tuple(color)
        template = template.replace('$color_%d' % i, vec4_color)
    return template


class BaseColormap(object):
    """Class representing a colormap:

        t \in [0, 1] --> rgba_color

    Parameters
    ----------
    colors : list of lists, tuples, or ndarrays
        The control colors used by the colormap (shape = (ncolors, 4)).

    Notes
    -----
    Must be overriden. Child classes need to implement:

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
            An array of values in [0,1].

        Returns
        -------
        rgba : ndarray
            An array with rgba values, with one color per item. The shape
            should be ``item.shape + (4,)``.

        Notes
        -----
        Users are expected to use a colormap with ``__getitem__()`` rather
        than ``map()`` (which implements a lower-level API).

        """
        raise NotImplementedError()

    def __getitem__(self, item):
        if isinstance(item, tuple):
            raise ValueError('ColorArray indexing is only allowed along '
                             'the first dimension.')
        # Ensure item is either a scalar or a column vector.
        item = _vector(item, type='column')
        # Clip the values in [0, 1].
        item = np.clip(item, 0., 1.)
        colors = self.map(item)
        return ColorArray(colors)

    def __setitem__(self, item, value):
        raise RuntimeError("It is not possible to set items to "
                           "BaseColormap instances.")

    def _repr_html_(self):
        n = 100
        html = ("""
                <style>
                    table.vispy_colormap {
                        height: 30px;
                        border: 0;
                        margin: 0;
                        padding: 0;
                    }

                    table.vispy_colormap td {
                        width: 3px;
                        border: 0;
                        margin: 0;
                        padding: 0;
                    }
                </style>
                <table class="vispy_colormap">
                """ +
                '\n'.join([(("""<td style="background-color: %s;"
                                 title="%s"></td>""") % (color, color))
                           for color in self[np.linspace(0., 1., n)].hex]) +
                """
                </table>
                """)
        return html


def _default_controls(ncolors):
    """Generate linearly spaced control points from a set of colors."""
    return np.linspace(0., 1., ncolors)


# List the parameters of every supported interpolation mode.
_interpolation_info = {
    'linear': {
        'ncontrols': lambda ncolors: ncolors,  # take ncolors as argument
        'glsl_map': _glsl_mix,  # take 'controls' as argument
        'map': mix,
    },
    'zero': {
        'ncontrols': lambda ncolors: (ncolors+1),
        'glsl_map': _glsl_step,
        'map': step,
    }
}


class Colormap(BaseColormap):
    """A colormap defining several control colors and an interpolation scheme.

    Parameters
    ----------
    colors : list of colors | ColorArray
        The list of control colors. If not a ``ColorArray``, a new
        ``ColorArray`` instance is created from this list. See the
        documentation of ``ColorArray``.
    controls : array-like
        The list of control points for the given colors. It should be
        an increasing list of floating-point number between 0.0 and 1.0.
        The first control point must be 0.0. The last control point must be
        1.0. The number of control points depends on the interpolation scheme.
    interpolation : str
        The interpolation mode of the colormap. Default: 'linear'. Can also
        be 'zero'.
        If 'linear', ncontrols = ncolors (one color per control point).
        If 'zero', ncontrols = ncolors+1 (one color per bin).

    Examples
    --------
    Here is a basic example:

        >>> from vispy.color import Colormap
        >>> cm = Colormap(['r', 'g', 'b'])
        >>> cm[0.], cm[0.5], cm[np.linspace(0., 1., 100)]

    """
    def __init__(self, colors, controls=None, interpolation='linear'):
        self.interpolation = interpolation
        ncontrols = self._ncontrols(len(colors))
        # Default controls.
        if controls is None:
            controls = _default_controls(ncontrols)
        assert len(controls) == ncontrols
        self._controls = np.array(controls, dtype=np.float32)
        self.glsl_map = self._glsl_map_generator(self._controls)
        super(Colormap, self).__init__(colors)

    @property
    def interpolation(self):
        """The interpolation mode of the colormap"""
        return self._interpolation

    @interpolation.setter
    def interpolation(self, val):
        if val not in _interpolation_info:
            raise ValueError('The interpolation mode can only be one of: ' +
                             ', '.join(sorted(_interpolation_info.keys())))
        # Get the information of the interpolation mode.
        info = _interpolation_info[val]
        # Get the function that generates the GLSL map, as a function of the
        # controls array.
        self._glsl_map_generator = info['glsl_map']
        # Number of controls as a function of the number of colors.
        self._ncontrols = info['ncontrols']
        # Python map function.
        self._map_function = info['map']
        self._interpolation = val

    def map(self, x):
        """The Python mapping function from the [0,1] interval to a
        list of rgba colors

        Parameters
        ----------
        x : array-like
            The values to map.

        Returns
        -------
        colors : list
            List of rgba colors.
        """
        return self._map_function(self.colors.rgba, x, self._controls)


class CubeHelixColormap(Colormap):
    def __init__(self, start=0.5, rot=1, gamma=1.0, reverse=True, nlev=32,
                 minSat=1.2, maxSat=1.2, minLight=0., maxLight=1., **kwargs):
        """Cube helix colormap

        A full implementation of Dave Green's "cubehelix" for Matplotlib.
        Based on the FORTRAN 77 code provided in
        D.A. Green, 2011, BASI, 39, 289.

        http://adsabs.harvard.edu/abs/2011arXiv1108.5083G

        User can adjust all parameters of the cubehelix algorithm.
        This enables much greater flexibility in choosing color maps, while
        always ensuring the color map scales in intensity from black
        to white. A few simple examples:

        Default color map settings produce the standard "cubehelix".

        Create color map in only blues by setting rot=0 and start=0.

        Create reverse (white to black) backwards through the rainbow once
        by setting rot=1 and reverse=True.

        Parameters
        ----------
        start : scalar, optional
            Sets the starting position in the color space. 0=blue, 1=red,
            2=green. Defaults to 0.5.
        rot : scalar, optional
            The number of rotations through the rainbow. Can be positive
            or negative, indicating direction of rainbow. Negative values
            correspond to Blue->Red direction. Defaults to -1.5
        gamma : scalar, optional
            The gamma correction for intensity. Defaults to 1.0
        reverse : boolean, optional
            Set to True to reverse the color map. Will go from black to
            white. Good for density plots where shade~density. Defaults to
            False
        nlev : scalar, optional
            Defines the number of discrete levels to render colors at.
            Defaults to 32.
        sat : scalar, optional
            The saturation intensity factor. Defaults to 1.2
            NOTE: this was formerly known as "hue" parameter
        minSat : scalar, optional
            Sets the minimum-level saturation. Defaults to 1.2
        maxSat : scalar, optional
            Sets the maximum-level saturation. Defaults to 1.2
        startHue : scalar, optional
            Sets the starting color, ranging from [0, 360], as in
            D3 version by @mbostock
            NOTE: overrides values in start parameter
        endHue : scalar, optional
            Sets the ending color, ranging from [0, 360], as in
            D3 version by @mbostock
            NOTE: overrides values in rot parameter
        minLight : scalar, optional
            Sets the minimum lightness value. Defaults to 0.
        maxLight : scalar, optional
            Sets the maximum lightness value. Defaults to 1.
        """
        super(CubeHelixColormap, self).__init__(
            cubehelix(start=start, rot=rot, gamma=gamma, reverse=reverse,
                      nlev=nlev, minSat=minSat, maxSat=maxSat,
                      minLight=minLight, maxLight=maxLight, **kwargs))


class _Fire(BaseColormap):
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


class _Grays(BaseColormap):
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


class _Ice(BaseColormap):
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


class _Hot(BaseColormap):
    colors = [(0., .33, .66, 1.0),
              (.33, .66, 1., 1.0)]

    glsl_map = """
    vec4 hot(float t) {
        return vec4(smoothstep($color_0.rgb, $color_1.rgb, vec3(t, t, t)),
                    1.0);
    }
    """

    def map(self, t):
        rgba = self.colors.rgba
        smoothed = smoothstep(rgba[0, :3], rgba[1, :3], t)
        return np.hstack((smoothed, np.ones((len(t), 1))))


class _Winter(BaseColormap):
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


class _SingleHue(Colormap):
    """A colormap which is solely defined by the given hue and value.

    Given the color hue and value, this color map increases the saturation
    of a color. The start color is almost white but still contains a hint of
    the given color, and at the end the color is fully saturated.

    Parameters
    ----------
    hue : scalar, optional
        The hue refers to a "true" color, without any shading or tinting.
        Must be in the range [0, 360]. Defaults to 200 (blue).
    saturation_range : array-like, optional
        The saturation represents how "pure" a color is. Less saturation means
        more white light mixed in the color. A fully saturated color means
        the pure color defined by the hue. No saturation means completely
        white. This colormap changes the saturation, and with this parameter
        you can specify the lower and upper bound. Default is [0.2, 0.8].
    value : scalar, optional
        The value defines the "brightness" of a color: a value of 0.0 means
        completely black while a value of 1.0 means the color defined by the
        hue without shading. Must be in the range [0, 1.0]. The default value
        is 1.0.

    Notes
    -----
    For more information about the hue values see the `wikipedia page`_.

    .. _wikipedia page: https://en.wikipedia.org/wiki/Hue
    """

    def __init__(self, hue=200, saturation_range=[0.1, 0.8], value=1.0):
        colors = ColorArray([
            (hue, saturation_range[0], value),
            (hue, saturation_range[1], value)
        ], color_space='hsv')
        super(_SingleHue, self).__init__(colors)


class _HSL(Colormap):
    """A colormap which is defined by n evenly spaced points in
    a circular color space.

    This means that we change the hue value while keeping the
    saturation and value constant.

    Parameters
    ---------
    n_colors : int, optional
        The number of colors to generate.
    hue_start : int, optional
        The hue start value. Must be in the range [0, 360], the default is 0.
    saturation : float, optional
        The saturation component of the colors to generate. The default is
        fully saturated (1.0). Must be in the range [0, 1.0].
    value : float, optional
        The value (brightness) component of the colors to generate. Must
        be in the range [0, 1.0], and the default is 1.0
    controls : array-like, optional
        The list of control points for the colors to generate. It should be
        an increasing list of floating-point number between 0.0 and 1.0.
        The first control point must be 0.0. The last control point must be
        1.0. The number of control points depends on the interpolation scheme.
    interpolation : str, optional
        The interpolation mode of the colormap. Default: 'linear'. Can also
        be 'zero'.
        If 'linear', ncontrols = ncolors (one color per control point).
        If 'zero', ncontrols = ncolors+1 (one color per bin).
    """

    def __init__(self, ncolors=6, hue_start=0, saturation=1.0, value=1.0,
                 controls=None, interpolation='linear'):
        hues = np.linspace(0, 360, ncolors + 1)[:-1]
        hues += hue_start
        hues %= 360

        colors = ColorArray([(hue, saturation, value) for hue in hues],
                            color_space='hsv')

        super(_HSL, self).__init__(colors, controls=controls,
                                   interpolation=interpolation)


class _HUSL(Colormap):
    """A colormap which is defined by n evenly spaced points in
    the HUSL hue space.

    Parameters
    ---------
    n_colors : int, optional
        The number of colors to generate.
    hue_start : int, optional
        The hue start value. Must be in the range [0, 360], the default is 0.
    saturation : float, optional
        The saturation component of the colors to generate. The default is
        fully saturated (1.0). Must be in the range [0, 1.0].
    value : float, optional
        The value component of the colors to generate or "brightness". Must
        be in the range [0, 1.0], and the default is 0.7.
    controls : array-like, optional
        The list of control points for the colors to generate. It should be
        an increasing list of floating-point number between 0.0 and 1.0.
        The first control point must be 0.0. The last control point must be
        1.0. The number of control points depends on the interpolation scheme.
    interpolation : str, optional
        The interpolation mode of the colormap. Default: 'linear'. Can also
        be 'zero'.
        If 'linear', ncontrols = ncolors (one color per control point).
        If 'zero', ncontrols = ncolors+1 (one color per bin).

    Notes
    -----
    For more information about HUSL colors see http://husl-colors.org
    """

    def __init__(self, ncolors=6, hue_start=0, saturation=1.0, value=0.7,
                 controls=None, interpolation='linear'):
        hues = np.linspace(0, 360, ncolors + 1)[:-1]
        hues += hue_start
        hues %= 360

        saturation *= 99
        value *= 99

        colors = ColorArray(
            [husl_to_rgb(hue, saturation, value) for hue in hues],
        )

        super(_HUSL, self).__init__(colors, controls=controls,
                                    interpolation=interpolation)


class _Diverging(Colormap):

    def __init__(self, h_pos=20, h_neg=250, saturation=1.0, value=0.7,
                 center="light"):
        saturation *= 99
        value *= 99

        start = husl_to_rgb(h_neg, saturation, value)
        mid = ((0.133, 0.133, 0.133) if center == "dark" else
               (0.92, 0.92, 0.92))
        end = husl_to_rgb(h_pos, saturation, value)

        colors = ColorArray([start, mid, end])

        super(_Diverging, self).__init__(colors)


_colormaps = dict(
    # Some colormap presets
    autumn=Colormap([(1., 0., 0., 1.), (1., 1., 0., 1.)]),
    blues=Colormap([(1., 1., 1., 1.), (0., 0., 1., 1.)]),
    cool=Colormap([(0., 1., 1., 1.), (1., 0., 1., 1.)]),
    greens=Colormap([(1., 1., 1., 1.), (0., 1., 0., 1.)]),
    reds=Colormap([(1., 1., 1., 1.), (1., 0., 0., 1.)]),
    spring=Colormap([(1., 0., 1., 1.), (1., 1., 0., 1.)]),
    summer=Colormap([(0., .5, .4, 1.), (1., 1., .4, 1.)]),
    fire=_Fire(),
    grays=_Grays(),
    hot=_Hot(),
    ice=_Ice(),
    winter=_Winter(),
    light_blues=_SingleHue(),
    orange=_SingleHue(hue=35),

    # Diverging presets
    coolwarm=Colormap(ColorArray(
        [
            (226, 0.59, 0.92), (222, 0.44, 0.99), (218, 0.26, 0.97),
            (30, 0.01, 0.87),
            (20, 0.3, 0.96), (15, 0.5, 0.95), (8, 0.66, 0.86)
        ],
        color_space="hsv"
    )),
    PuGr=_Diverging(145, 280, 0.85, 0.30),
    GrBu=_Diverging(255, 133, 0.75, 0.6),
    GrBu_d=_Diverging(255, 133, 0.75, 0.6, "dark"),
    RdBu=_Diverging(220, 20, 0.75, 0.5),

    # Configurable colormaps
    cubehelix=CubeHelixColormap(),
    single_hue=_SingleHue,
    hsl=_HSL,
    husl=_HUSL,
    diverging=_Diverging
)


def get_colormap(name, *args, **kwargs):
    """Obtain a colormap

    Some colormaps can have additional configuration parameters. Refer to
    their corresponding documentation for more information.

    Parameters
    ----------
    name : str | Colormap
        Colormap name. Can also be a Colormap for pass-through.

    Examples
    --------

        >>> get_colormap('autumn')
        >>> get_colormap('single_hue', hue=10)
    """
    if isinstance(name, BaseColormap):
        cmap = name
    else:
        if not isinstance(name, string_types):
            raise TypeError('colormap must be a Colormap or string name')
        if name not in _colormaps:
            raise KeyError('colormap name %s not found' % name)
        cmap = _colormaps[name]

        if inspect.isclass(cmap):
            cmap = cmap(*args, **kwargs)

    return cmap


def get_colormaps():
    """Return the list of colormap names."""
    return _colormaps.copy()
