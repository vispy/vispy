# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ...util import transforms
from ...geometry import Rect
from ._util import arg_to_vec4, as_vec4
from .base_transform import BaseTransform


class NullTransform(BaseTransform):
    """Transform having no effect on coordinates (identity transform)."""

    glsl_map = "vec4 null_transform_map(vec4 pos) {return pos;}"
    glsl_imap = "vec4 null_transform_imap(vec4 pos) {return pos;}"

    Linear = True
    Orthogonal = True
    NonScaling = True
    Isometric = True

    @arg_to_vec4
    def map(self, coords):
        """Map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to map.
        """
        return coords

    def imap(self, coords):
        """Inverse map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to inverse map.
        """
        return coords

    def __mul__(self, tr):
        return tr

    def __rmul__(self, tr):
        return tr


class STTransform(BaseTransform):
    """Transform performing only scale and translate, in that order.

    Parameters
    ----------
    scale : array-like
        Scale factors for X, Y, Z axes.
    translate : array-like
        Scale factors for X, Y, Z axes.
    """

    glsl_map = """
        vec4 st_transform_map(vec4 pos) {
            return vec4(pos.xyz * $scale.xyz + $translate.xyz * pos.w, pos.w);
        }
    """

    glsl_imap = """
        vec4 st_transform_imap(vec4 pos) {
            return vec4((pos.xyz - $translate.xyz * pos.w) / $scale.xyz,
                        pos.w);
        }
    """

    Linear = True
    Orthogonal = True
    NonScaling = False
    Isometric = False

    def __init__(self, scale=None, translate=None):
        super(STTransform, self).__init__()

        self._scale = np.ones(4, dtype=np.float32)
        self._translate = np.zeros(4, dtype=np.float32)

        s = ((1.0, 1.0, 1.0, 1.0) if scale is None else
             as_vec4(scale, default=(1., 1., 1., 1.)))
        t = ((0.0, 0.0, 0.0, 0.0) if translate is None else
             as_vec4(translate, default=(0., 0., 0., 0.)))
        self._set_st(s, t)
        self._update_shaders()

    @arg_to_vec4
    def map(self, coords):
        """Map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to map.

        Returns
        -------
        coords : ndarray
            Coordinates.
        """
        m = np.empty(coords.shape)
        m[:, :3] = (coords[:, :3] * self.scale[np.newaxis, :3] +
                    coords[:, 3:] * self.translate[np.newaxis, :3])
        m[:, 3] = coords[:, 3]
        return m

    @arg_to_vec4
    def imap(self, coords):
        """Invert map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to inverse map.

        Returns
        -------
        coords : ndarray
            Coordinates.
        """
        m = np.empty(coords.shape)
        m[:, :3] = ((coords[:, :3] -
                     coords[:, 3:] * self.translate[np.newaxis, :3]) /
                    self.scale[np.newaxis, :3])
        m[:, 3] = coords[:, 3]
        return m

    def shader_map(self):
        return self._shader_map

    def shader_imap(self):
        return self._shader_imap

    @property
    def scale(self):
        return self._scale.copy()

    @scale.setter
    def scale(self, s):
        s = as_vec4(s, default=(1, 1, 1, 1))
        self._set_st(scale=s)

    @property
    def translate(self):
        return self._translate.copy()

    @translate.setter
    def translate(self, t):
        t = as_vec4(t, default=(0, 0, 0, 0))
        self._set_st(translate=t)

    def _set_st(self, scale=None, translate=None, update=True):
        need_update = False

        if scale is not None and not np.all(scale == self._scale):
            self._scale[:] = scale
            need_update = True

        if translate is not None and not np.all(translate == self._translate):
            self._translate[:] = translate
            need_update = True

        if update and need_update:
            self._update_shaders()
            self.update()   # inform listeners there has been a change

    def _update_shaders(self):
        self._shader_map['scale'] = self.scale
        self._shader_map['translate'] = self.translate
        self._shader_imap['scale'] = self.scale
        self._shader_imap['translate'] = self.translate

    def move(self, move):
        """Change the translation of this transform by the amount given.

        Parameters
        ----------
        move : array-like
            The values to be added to the current translation of the transform.
        """
        move = as_vec4(move, default=(0, 0, 0, 0))
        self.translate = self.translate + move

    def zoom(self, zoom, center=(0, 0, 0), mapped=True):
        """Update the transform such that its scale factor is changed, but
        the specified center point is left unchanged.

        Parameters
        ----------
        zoom : array-like
            Values to multiply the transform's current scale
            factors.
        center : array-like
            The center point around which the scaling will take place.
        mapped : bool
            Whether *center* is expressed in mapped coordinates (True) or
            unmapped coordinates (False).
        """
        zoom = as_vec4(zoom, default=(1, 1, 1, 1))
        center = as_vec4(center, default=(0, 0, 0, 0))
        scale = self.scale * zoom
        if mapped:
            trans = center - (center - self.translate) * zoom
        else:
            trans = self.scale * (1 - zoom) * center + self.translate
        self._set_st(scale=scale, translate=trans)

    def as_matrix(self):
        m = MatrixTransform()
        m.scale(self.scale)
        m.translate(self.translate)
        return m

    @classmethod
    def from_mapping(cls, x0, x1):
        """Create an STTransform from the given mapping

        See `set_mapping` for details.

        Parameters
        ----------
        x0 : array-like
            Start.
        x1 : array-like
            End.

        Returns
        -------
        t : instance of STTransform
            The transform.
        """
        t = cls()
        t.set_mapping(x0, x1)
        return t

    def set_mapping(self, x0, x1, update=True):
        """Configure this transform such that it maps points x0 => x1

        Parameters
        ----------
        x0 : array-like, shape (2, 2) or (2, 3)
            Start location.
        x1 : array-like, shape (2, 2) or (2, 3)
            End location.
        update : bool
            If False, then the update event is not emitted.

        Examples
        --------
        For example, if we wish to map the corners of a rectangle::

            >>> p1 = [[0, 0], [200, 300]]

        onto a unit cube::

            >>> p2 = [[-1, -1], [1, 1]]

        then we can generate the transform as follows::

            >>> tr = STTransform()
            >>> tr.set_mapping(p1, p2)
            >>> assert tr.map(p1)[:,:2] == p2  # test
        """
        # if args are Rect, convert to array first
        if isinstance(x0, Rect):
            x0 = x0._transform_in()[:3]
        if isinstance(x1, Rect):
            x1 = x1._transform_in()[:3]

        x0 = np.asarray(x0)
        x1 = np.asarray(x1)
        if (x0.ndim != 2 or x0.shape[0] != 2 or x1.ndim != 2 or
                x1.shape[0] != 2):
            raise TypeError("set_mapping requires array inputs of shape "
                            "(2, N).")
        denom = x0[1] - x0[0]
        mask = denom == 0
        denom[mask] = 1.0
        s = (x1[1] - x1[0]) / denom
        s[mask] = 1.0
        s[x0[1] == x0[0]] = 1.0
        t = x1[0] - s * x0[0]
        s = as_vec4(s, default=(1, 1, 1, 1))
        t = as_vec4(t, default=(0, 0, 0, 0))
        self._set_st(scale=s, translate=t, update=update)

    def __mul__(self, tr):
        if isinstance(tr, STTransform):
            s = self.scale * tr.scale
            t = self.translate + (tr.translate * self.scale)
            return STTransform(scale=s, translate=t)
        elif isinstance(tr, MatrixTransform):
            return self.as_matrix() * tr
        else:
            return super(STTransform, self).__mul__(tr)

    def __rmul__(self, tr):
        if isinstance(tr, MatrixTransform):
            return tr * self.as_matrix()
        return super(STTransform, self).__rmul__(tr)

    def __repr__(self):
        return ("<STTransform scale=%s translate=%s at 0x%s>"
                % (self.scale, self.translate, id(self)))


class MatrixTransform(BaseTransform):
    """Affine transformation class

    Parameters
    ----------
    matrix : array-like | None
        4x4 array to use for the transform.
    """

    glsl_map = """
        vec4 affine_transform_map(vec4 pos) {
            return $matrix * pos;
        }
    """

    glsl_imap = """
        vec4 affine_transform_imap(vec4 pos) {
            return $inv_matrix * pos;
        }
    """

    Linear = True
    Orthogonal = False
    NonScaling = False
    Isometric = False

    def __init__(self, matrix=None):
        super(MatrixTransform, self).__init__()
        if matrix is not None:
            self.matrix = matrix
        else:
            self.reset()

    @arg_to_vec4
    def map(self, coords):
        """Map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to map.

        Returns
        -------
        coords : ndarray
            Coordinates.
        """
        # looks backwards, but both matrices are transposed.
        return np.dot(coords, self.matrix)

    @arg_to_vec4
    def imap(self, coords):
        """Inverse map coordinates

        Parameters
        ----------
        coords : array-like
            Coordinates to inverse map.

        Returns
        -------
        coords : ndarray
            Coordinates.
        """
        return np.dot(coords, self.inv_matrix)

    def shader_map(self):
        fn = super(MatrixTransform, self).shader_map()
        fn['matrix'] = self.matrix  # uniform mat4
        return fn

    def shader_imap(self):
        fn = super(MatrixTransform, self).shader_imap()
        fn['inv_matrix'] = self.inv_matrix  # uniform mat4
        return fn

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, m):
        self._matrix = m
        self._inv_matrix = None
        self.shader_map()
        self.shader_imap()
        self.update()

    @property
    def inv_matrix(self):
        if self._inv_matrix is None:
            self._inv_matrix = np.linalg.inv(self.matrix)
        return self._inv_matrix

    @arg_to_vec4
    def translate(self, pos):
        """
        Translate the matrix

        The translation is applied *after* the transformations already present
        in the matrix.

        Parameters
        ----------
        pos : arrayndarray
            Position to translate by.
        """
        self.matrix = np.dot(self.matrix, transforms.translate(pos[0, :3]))

    def scale(self, scale, center=None):
        """
        Scale the matrix about a given origin.

        The scaling is applied *after* the transformations already present
        in the matrix.

        Parameters
        ----------
        scale : array-like
            Scale factors along x, y and z axes.
        center : array-like or None
            The x, y and z coordinates to scale around. If None,
            (0, 0, 0) will be used.
        """
        scale = transforms.scale(as_vec4(scale, default=(1, 1, 1, 1))[0, :3])
        if center is not None:
            center = as_vec4(center)[0, :3]
            scale = np.dot(np.dot(transforms.translate(-center), scale),
                           transforms.translate(center))
        self.matrix = np.dot(self.matrix, scale)

    def rotate(self, angle, axis):
        """
        Rotate the matrix by some angle about a given axis.

        The rotation is applied *after* the transformations already present
        in the matrix.

        Parameters
        ----------
        angle : float
            The angle of rotation, in degrees.
        axis : array-like
            The x, y and z coordinates of the axis vector to rotate around.
        """
        self.matrix = np.dot(self.matrix, transforms.rotate(angle, axis))

    def set_mapping(self, points1, points2):
        """Set to a 3D transformation matrix that maps points1 onto points2.

        Parameters
        ----------
        points1 : array-like, shape (4, 3)
            Four starting 3D coordinates.
        points2 : array-like, shape (4, 3)
            Four ending 3D coordinates.
        """
        # note: need to transpose because util.functions uses opposite
        # of standard linear algebra order.
        self.matrix = transforms.affine_map(points1, points2).T

    def set_ortho(self, l, r, b, t, n, f):  # noqa
        """Set ortho transform

        Parameters
        ----------
        l : float
            Left.
        r : float
            Right.
        b : float
            Bottom.
        t : float
            Top.
        n : float
            Near.
        f : float
            Far.
        """
        self.matrix = transforms.ortho(l, r, b, t, n, f)

    def reset(self):
        self.matrix = np.eye(4)

    def __mul__(self, tr):
        if (isinstance(tr, MatrixTransform) and not
                any(tr.matrix[:3, 3] != 0)):
            # don't multiply if the perspective column is used
            return MatrixTransform(matrix=np.dot(tr.matrix, self.matrix))
        else:
            return tr.__rmul__(self)

    def __repr__(self):
        s = "%s(matrix=[" % self.__class__.__name__
        indent = " "*len(s)
        s += str(list(self.matrix[0])) + ",\n"
        s += indent + str(list(self.matrix[1])) + ",\n"
        s += indent + str(list(self.matrix[2])) + ",\n"
        s += indent + str(list(self.matrix[3])) + "] at 0x%x)" % id(self)
        return s

    def set_perspective(self, fov, aspect, near, far):
        """Set the perspective

        Parameters
        ----------
        fov : float
            Field of view.
        aspect : float
            Aspect ratio.
        near : float
            Near location.
        far : float
            Far location.
        """
        self.matrix = transforms.perspective(fov, aspect, near, far)

    def set_frustum(self, l, r, b, t, n, f):  # noqa
        """Set the frustum

        Parameters
        ----------
        l : float
            Left.
        r : float
            Right.
        b : float
            Bottom.
        t : float
            Top.
        n : float
            Near.
        f : float
            Far.
        """
        self.matrix = transforms.frustum(l, r, b, t, n, f)


# class SRTTransform(BaseTransform):
#    """ Transform performing scale, rotate, and translate, in that order.
#
#    This transformation allows objects to be placed arbitrarily in a scene
#    much the same way MatrixTransform does. However, an incorrect order of
#    operations in MatrixTransform may result in shearing the object (if scale
#    is applied after rotate) or in unpredictable translation (if scale/rotate
#    is applied after translation). SRTTransform avoids these problems by
#    enforcing the correct order of operations.
#    """
#    # TODO
