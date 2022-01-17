# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ._util import arg_to_array, arg_to_vec4, as_vec4
from .base_transform import BaseTransform
from ... import gloo


class LogTransform(BaseTransform):
    """Transform perfoming logarithmic transformation on three axes.

    Maps (x, y, z) => (log(base.x, x), log(base.y, y), log(base.z, z))

    No transformation is applied for axes with base == 0.

    If base < 0, then the inverse function is applied: x => base.x ** x

    Parameters
    ----------
    base : array-like
        Base for the X, Y, Z axes.
    """

    # TODO: Evaluate the performance costs of using conditionals.
    # An alternative approach is to transpose the vector before
    # log-transforming, and then transpose back afterward.
    glsl_map = """
        vec4 LogTransform_map(vec4 pos) {
            if($base.x > 1.0)
                pos.x = log(pos.x) / log($base.x);
            else if($base.x < -1.0)
                pos.x = pow(-$base.x, pos.x);

            if($base.y > 1.0)
                pos.y = log(pos.y) / log($base.y);
            else if($base.y < -1.0)
                pos.y = pow(-$base.y, pos.y);

            if($base.z > 1.0)
                pos.z = log(pos.z) / log($base.z);
            else if($base.z < -1.0)
                pos.z = pow(-$base.z, pos.z);
            return pos;
        }
        """

    glsl_imap = glsl_map

    Linear = False
    Orthogonal = True
    NonScaling = False
    Isometric = False

    def __init__(self, base=None):
        super(LogTransform, self).__init__()
        self._base = np.zeros(3, dtype=np.float32)
        self.base = (0.0, 0.0, 0.0) if base is None else base

    @property
    def base(self):
        """
        *base* is a tuple (x, y, z) containing the log base that should be
        applied to each axis of the input vector. If any axis has a base <= 0,
        then that axis is not affected.
        """
        return self._base.copy()

    @base.setter
    def base(self, s):
        self._base[:len(s)] = s
        self._base[len(s):] = 0.0

    @arg_to_array
    def map(self, coords, base=None):
        ret = np.empty(coords.shape, coords.dtype)
        if base is None:
            base = self.base
        for i in range(min(ret.shape[-1], 3)):
            if base[i] > 1.0:
                ret[..., i] = np.log(coords[..., i]) / np.log(base[i])
            elif base[i] < -1.0:
                ret[..., i] = -base[i] ** coords[..., i]
            else:
                ret[..., i] = coords[..., i]
        return ret

    @arg_to_array
    def imap(self, coords):
        return self.map(coords, -self.base)

    def shader_map(self):
        fn = super(LogTransform, self).shader_map()
        fn['base'] = self.base  # uniform vec3
        return fn

    def shader_imap(self):
        fn = super(LogTransform, self).shader_imap()
        fn['base'] = -self.base  # uniform vec3
        return fn

    def __repr__(self):
        return "<LogTransform base=%s>" % (self.base)


class PolarTransform(BaseTransform):
    """Polar transform

    Maps (theta, r, z) to (x, y, z), where `x = r*cos(theta)`
    and `y = r*sin(theta)`.
    """

    glsl_map = """
        vec4 polar_transform_map(vec4 pos) {
            return vec4(pos.y * cos(pos.x), pos.y * sin(pos.x), pos.z, 1.);
        }
        """

    glsl_imap = """
        vec4 polar_transform_map(vec4 pos) {
            // TODO: need some modulo math to handle larger theta values..?
            float theta = atan(pos.y, pos.x);
            float r = length(pos.xy);
            return vec4(theta, r, pos.z, 1.);
        }
        """

    Linear = False
    Orthogonal = False
    NonScaling = False
    Isometric = False

    @arg_to_array
    def map(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        ret[..., 0] = coords[..., 1] * np.cos(coords[..., 0])
        ret[..., 1] = coords[..., 1] * np.sin(coords[..., 0])
        for i in range(2, coords.shape[-1]):  # copy any further axes
            ret[..., i] = coords[..., i]
        return ret

    @arg_to_array
    def imap(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        ret[..., 0] = np.arctan2(coords[..., 0], coords[..., 1])
        ret[..., 1] = (coords[..., 0]**2 + coords[..., 1]**2) ** 0.5
        for i in range(2, coords.shape[-1]):  # copy any further axes
            ret[..., i] = coords[..., i]
        return ret


# class BilinearTransform(BaseTransform):
#    # TODO
#    pass


# class WarpTransform(BaseTransform):
#    """ Multiple bilinear transforms in a grid arrangement.
#    """
#    # TODO


class MagnifyTransform(BaseTransform):
    """Magnifying lens transform. 

    This transform causes a circular region to appear with larger scale around
    its center point. 

    Parameters
    ----------
    mag : float
        Magnification factor. Objects around the transform's center point will
        appear scaled by this amount relative to objects outside the circle.
    radii : (float, float)
        Inner and outer radii of the "lens". Objects inside the inner radius
        appear scaled, whereas objects outside the outer radius are unscaled,
        and the scale factor transitions smoothly between the two radii.
    center: (float, float)
        The center (x, y) point of the "lens".

    Notes
    -----
    This transform works by segmenting its input coordinates into three
    regions--inner, outer, and transition. Coordinates in the inner region are
    multiplied by a constant scale factor around the center point, and 
    coordinates in the transition region are scaled by a factor that 
    transitions smoothly from the inner radius to the outer radius. 

    Smooth functions that are appropriate for the transition region also tend 
    to be difficult to invert analytically, so this transform instead samples
    the function numerically to allow trivial inversion. In OpenGL, the 
    sampling is implemented as a texture holding a lookup table.
    """

    glsl_map = """
        vec4 mag_transform(vec4 pos) {
            vec2 d = vec2(pos.x - $center.x, pos.y - $center.y);
            float dist = length(d);
            if (dist == 0. || dist > $radii.y || ($mag<1.01 && $mag>0.99)) {
                return pos;
            }
            vec2 dir = d / dist;
            
            if( dist < $radii.x ) {
                dist = dist * $mag;
            }
            else {
                
                float r1 = $radii.x;
                float r2 = $radii.y;
                float x = (dist - r1) / (r2 - r1);
                float s = texture2D($trans, vec2(0., x)).r * $trans_max;
                
                dist = s;
            }

            d = $center + dir * dist;
            return vec4(d, pos.z, pos.w);
        }"""

    glsl_imap = glsl_map

    Linear = False

    _trans_resolution = 1000

    def __init__(self, mag=3, radii=(7, 10), center=(0, 0)):
        self._center = center
        self._mag = mag
        self._radii = radii
        self._trans = None
        res = self._trans_resolution
        self._trans_tex = (gloo.Texture2D((res, 1, 1), interpolation='linear'), 
                           gloo.Texture2D((res, 1, 1), interpolation='linear'))
        self._trans_tex_max = None
        super(MagnifyTransform, self).__init__()

    @property
    def center(self):
        """The (x, y) center point of the transform."""
        return self._center

    @center.setter
    def center(self, center):
        if np.allclose(self._center, center):
            return
        self._center = center
        self.shader_map()
        self.shader_imap()

    @property
    def mag(self):
        """The scale factor used in the central region of the transform."""
        return self._mag

    @mag.setter
    def mag(self, mag):
        if self._mag == mag:
            return
        self._mag = mag
        self._trans = None
        self.shader_map()
        self.shader_imap()

    @property
    def radii(self):
        """The inner and outer radii of the circular area bounding the transform."""
        return self._radii

    @radii.setter
    def radii(self, radii):
        if np.allclose(self._radii, radii):
            return
        self._radii = radii
        self._trans = None
        self.shader_map()
        self.shader_imap()

    def shader_map(self):
        fn = super(MagnifyTransform, self).shader_map()
        fn['center'] = self._center  # uniform vec2
        fn['mag'] = float(self._mag)
        fn['radii'] = (self._radii[0] / float(self._mag), self._radii[1])
        self._get_transition()  # make sure transition texture is up to date
        fn['trans'] = self._trans_tex[0]
        fn['trans_max'] = self._trans_tex_max[0]
        return fn

    def shader_imap(self):
        fn = super(MagnifyTransform, self).shader_imap()
        fn['center'] = self._center  # uniform vec2
        fn['mag'] = 1. / self._mag
        fn['radii'] = self._radii
        self._get_transition()  # make sure transition texture is up to date
        fn['trans'] = self._trans_tex[1]
        fn['trans_max'] = self._trans_tex_max[1]
        return fn

    @arg_to_vec4
    def map(self, x, _inverse=False):
        c = as_vec4(self.center)[0]
        m = self.mag
        r1, r2 = self.radii

        xm = np.empty(x.shape, dtype=x.dtype)

        dx = (x - c)
        dist = (((dx**2).sum(axis=-1)) ** 0.5)[..., np.newaxis]
        dist[np.isnan(dist)] = 0
        unit = dx / np.where(dist != 0, dist, 1)
        # magnified center region
        if _inverse:
            inner = (dist < r1)[:, 0]
            s = dist / m
        else:
            inner = (dist < (r1 / m))[:, 0]
            s = dist * m
        xm[inner] = c + unit[inner] * s[inner]

        # unmagnified outer region
        outer = (dist > r2)[:, 0]  
        xm[outer] = x[outer]

        # smooth transition region, interpolated from trans
        trans = ~(inner | outer)

        # look up scale factor from trans
        temp, itemp = self._get_transition()
        if _inverse:
            tind = (dist[trans] - r1) * len(itemp) / (r2 - r1)
            temp = itemp
        else:
            tind = (dist[trans] - (r1/m)) * len(temp) / (r2 - (r1/m))
        tind = np.clip(tind, 0, temp.shape[0]-1)
        s = temp[tind.astype(int)]

        xm[trans] = c + unit[trans] * s
        return xm

    def imap(self, coords):
        return self.map(coords, _inverse=True)

    def _get_transition(self):
        # Generate forward/reverse transition templates.
        # We would prefer to express this with an invertible function, but that
        # turns out to be tricky. The templates make any function invertible.

        if self._trans is None:
            m, r1, r2 = self.mag, self.radii[0], self.radii[1]
            res = self._trans_resolution

            xi = np.linspace(r1, r2, res)
            t = 0.5 * (1 + np.cos((xi - r2) * np.pi / (r2 - r1)))
            yi = (xi * t + xi * (1-t) / m).astype(np.float32)
            x = np.linspace(r1 / m, r2, res)
            y = np.interp(x, yi, xi).astype(np.float32)

            self._trans = (y, yi)
            # scale to 0.0-1.0 to prevent clipping (is this necessary?)
            mx = y.max(), yi.max()
            self._trans_tex_max = mx
            self._trans_tex[0].set_data((y/mx[0])[:, np.newaxis, np.newaxis])
            self._trans_tex[1].set_data((yi/mx[1])[:, np.newaxis, np.newaxis])

        return self._trans


class Magnify1DTransform(MagnifyTransform):
    """A 1-dimensional analog of MagnifyTransform. This transform expands 
    its input along the x-axis, around a center x value.
    """

    glsl_map = """
        vec4 mag_transform(vec4 pos) {
            float dist = pos.x - $center.x;
            if (dist == 0. || abs(dist) > $radii.y || $mag == 1) {
                return pos;
            }
            float dir = dist / abs(dist);
            
            if( abs(dist) < $radii.x ) {
                dist = dist * $mag;
            }
            else {
                float r1 = $radii.x;
                float r2 = $radii.y;
                float x = (abs(dist) - r1) / (r2 - r1);
                dist = dir * texture2D($trans, vec2(0., x)).r * $trans_max;
            }

            return vec4($center.x + dist, pos.y, pos.z, pos.w);
        }"""

    glsl_imap = glsl_map
