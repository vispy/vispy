# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import re
import math
import numpy as np

# ------------------------------------------------------------------ Matrix ---


class Matrix(object):

    def __init__(self, a=1, b=0, c=0, d=1, e=0, f=0):
        self._matrix = np.array([[a, c, e],
                                 [b, d, f],
                                 [0, 0, 1]], dtype=float)

    @property
    def matrix(self):
        return self._matrix

    def __array__(self, *args):
        return self._matrix

    def __repr__(self):
        a, c, e = self._matrix[0]
        b, d, f = self._matrix[1]
        return "Matrix(%g,%g,%g,%g,%g,%g)" % (a, b, c, d, e, f)


# ---------------------------------------------------------------- Identity ---
class Identity(Matrix):

    def __init__(self):
        Matrix.__init__(self)
        self._matrix[...] = ([[1, 0, 0],
                              [0, 1, 0],
                              [0, 0, 1]])

    def __repr__(self):
        return "Identity()"


# --------------------------------------------------------------- Translate ---
class Translate(Matrix):
    """
    Translation is equivalent to the matrix [1 0 0 1 tx ty], where tx and ty
    are the distances to translate coordinates in X and Y, respectively.
    """

    def __init__(self, x, y=0):
        Matrix.__init__(self)
        self._x, self._y = x, y
        self._matrix[...] = ([[1, 0, x],
                              [0, 1, y],
                              [0, 0, 1]])

    def __repr__(self):
        return "Translate(%g,%g)" % (self._x, self._y)


# ------------------------------------------------------------------- Scale ---
class Scale(Matrix):
    """
    Scaling is equivalent to the matrix [sx 0 0 sy 0 0]. One unit in the X and
    Y directions in the new coordinate system equals sx and sy units in the
    previous coordinate system, respectively.
    """

    def __init__(self, x, y=0):
        Matrix.__init__(self)
        self._x = x
        self._y = y or x
        self._matrix[...] = ([[x, 0, 0],
                              [0, y, 0],
                              [0, 0, 1]])

    def __repr__(self):
        return "Scale(%g,%g)" % (self._x, self._y)


# ------------------------------------------------------------------- Scale ---
class Rotate(Matrix):
    """
    Rotation about the origin is equivalent to the matrix [cos(a) sin(a)
    -sin(a) cos(a) 0 0], which has the effect of rotating the coordinate system
    axes by angle a.
    """

    def __init__(self, angle, x=0, y=0):
        Matrix.__init__(self)
        self._angle = angle
        self._x = x
        self._y = y

        angle = math.pi * angle / 180.0
        rotate = np.array([[math.cos(angle), -math.sin(angle), 0],
                           [math.sin(angle), math.cos(angle), 0],
                           [0, 0, 1]], dtype=float)
        forward = np.array([[1, 0, x],
                            [0, 1, y],
                            [0, 0, 1]], dtype=float)
        inverse = np.array([[1, 0, -x],
                            [0, 1, -y],
                            [0, 0, 1]], dtype=float)
        self._matrix = np.dot(inverse, np.dot(rotate, forward))

    def __repr__(self):
        return "Rotate(%g,%g,%g)" % (self._angle, self._x, self._y)


# ------------------------------------------------------------------- SkewX ---
class SkewX(Matrix):
    """
    A skew transformation along the x-axis is equivalent to the matrix [1 0
    tan(a) 1 0 0], which has the effect of skewing X coordinates by angle a.
    """

    def __init__(self, angle):
        Matrix.__init__(self)
        self._angle = angle
        angle = math.pi * angle / 180.0
        self._matrix[...] = ([[1, math.tan(angle), 0],
                              [0, 1, 0],
                              [0, 0, 1]])

    def __repr__(self):
        return "SkewX(%g)" % (self._angle)


# ------------------------------------------------------------------- SkewY ---
class SkewY(Matrix):
    """
    A skew transformation along the y-axis is equivalent to the matrix [1
    tan(a) 0 1 0 0], which has the effect of skewing Y coordinates by angle a.
    """

    def __init__(self, angle):
        Matrix.__init__(self)
        self._angle = angle
        angle = math.pi * angle / 180.0
        self._matrix[...] = ([[1, 0, 0],
                              [math.tan(angle), 1, 0],
                              [0, 0, 1]])

    def __repr__(self):
        return "SkewY(%g)" % (self._angle)


# --------------------------------------------------------------- Transform ---
class Transform(object):
    """
    A Transform is defined as a list of transform definitions, which are
    applied in the order provided. The individual transform definitions are
    separated by whitespace and/or a comma.
    """

    def __init__(self, content=""):
        self._transforms = []
        if not content:
            return

        converters = {"matrix": Matrix,
                      "scale": Scale,
                      "rotate": Rotate,
                      "translate": Translate,
                      "skewx": SkewX,
                      "skewy": SkewY}
        keys = "|".join(converters.keys())
        pattern = r"(?P<name>%s)\s*\((?P<args>[^)]*)\)" % keys

        for match in re.finditer(pattern, content):
            name = match.group("name").strip()
            args = match.group("args").strip().replace(',', ' ')
            args = [float(value) for value in args.split()]
            transform = converters[name](*args)
            self._transforms.append(transform)

    def __add__(self, other):
        T = Transform()
        T._transforms.extend(self._transforms)
        T._transforms.extend(other._transforms)
        return T

    def __radd__(self, other):
        self._transforms.extend(other._transforms)
        return self

    @property
    def matrix(self):
        M = np.eye(3)
        for transform in self._transforms:
            M = np.dot(M, transform)
        return M

    def __array__(self, *args):
        return self._matrix

    def __repr__(self):
        s = ""
        for i in range(len(self._transforms)):
            s += repr(self._transforms[i])
            if i < len(self._transforms) - 1:
                s += ", "
        return s

    @property
    def xml(self):
        return self._xml()

    def _xml(self, prefix=""):

        identity = True
        for transform in self._transforms:
            if not isinstance(transform, Identity):
                identity = False
                break
        if identity:
            return ""

        return 'transform="%s" ' % repr(self)
