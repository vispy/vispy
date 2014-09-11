# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ._util import arg_to_array
from .base_transform import BaseTransform


class LogTransform(BaseTransform):
    """ Transform perfoming logarithmic transformation on three axes.

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
        for i in range(ret.shape[-1]):
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
            return vec4(pos.y * cos(pos.x), pos.y * sin(pos.x), pos.z, 1);
        }
        """

    glsl_imap = """
        vec4 polar_transform_map(vec4 pos) {
            // TODO: need some modulo math to handle larger theta values..?
            float theta = atan(pos.y, pos.x);
            float r = length(pos.xy);
            return vec4(theta, r, pos.z, 1);
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


#class BilinearTransform(BaseTransform):
#    # TODO
#    pass


#class WarpTransform(BaseTransform):
#    """ Multiple bilinear transforms in a grid arrangement.
#    """
#    # TODO
