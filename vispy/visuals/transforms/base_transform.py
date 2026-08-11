# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
API Issues to work out:

  - MatrixTransform and STTransform both have 'scale' and 'translate'
    attributes, but they are used in very different ways. It would be nice
    to keep this consistent, but how?

  - Need a transform.map_rect function that returns the bounding rectangle of
    a rect after transformation. Non-linear transforms might need to work
    harder at this, but we can provide a default implementation that
    works by mapping a selection of points across a grid within the original
    rect.
"""

from __future__ import division

from ._util import InverseKind
from ..shaders import Function
from ...util.event import EventEmitter


class BaseTransform(object):
    """
    A transform may therefore support forward mapping without supporting
    inverse mapping, or may support an inverse on the CPU without providing
    a GLSL implementation.

    BaseTransform is a base class that defines a pair of complementary
    coordinate mapping functions in both python and GLSL.

    All BaseTransform subclasses provide a forward coordinate mapping via
    map() and may provide an inverse mapping via imap().

    glsl_map defines the forward GLSL mapping when GPU mapping is
    supported. glsl_imap optionally defines the inverse GLSL mapping.
    Both are instances of shaders.Function.

    Optionally, an inverse() method returns a new transform performing the
    inverse mapping. The inverse_kind attribute indicates whether an inverse
    mapping is exact, approximate, or unavailable.
    """

    glsl_map = None  # Must be GLSL code
    glsl_imap = None

    # Flags used to describe the transformation. Subclasses should define each
    # as True or False.
    # (usually used for making optimization decisions)

    # If True, then for any 3 colinear points, the
    # transformed points will also be colinear.
    Linear = None

    # The transformation's effect on one axis is independent
    # of the input position along any other axis.
    Orthogonal = None

    # If True, then the distance between two points is the
    # same as the distance between the transformed points.
    NonScaling = None

    # Scale factors are applied equally to all axes.
    Isometric = None

    # For linear transforms, exact by default, but for non-linear transforms can be different.
    inverse_kind = InverseKind.EXACT

    def __init__(self):
        self._inverse = None
        self._dynamic = False
        self.changed = EventEmitter(source=self, type='transform_changed')
        self._shader_map = (
            Function(self.glsl_map)
            if self.glsl_map is not None
            else None
        )

        self._shader_imap = (
            Function(self.glsl_imap)
            if self.glsl_imap is not None
            else None
        )

    def map(self, obj):
        """
        Return *obj* mapped through the forward transformation.

        Parameters
        ----------
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        raise NotImplementedError()

    def imap(self, obj):
        """
        Return *obj* mapped through the inverse transformation.

        Parameters
        ----------
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        if self.inverse_kind is InverseKind.NONE:
            raise NotImplementedError(
                f"{type(self).__name__} does not implement imap()"
            )
        raise NotImplementedError()

    @property
    def inverse(self):
        """The inverse of this transform."""
        if self.inverse_kind is InverseKind.NONE:
            raise NotImplementedError(
                f"{type(self).__name__} does not provide an inverse transform"
            )
        if self._inverse is None:
            self._inverse = InverseTransform(self)
        return self._inverse

    @property
    def dynamic(self):
        """Boolean flag that indicates whether this transform is expected to 
        change frequently.

        Transforms that are flagged as dynamic will not be collapsed in 
        ``ChainTransform.simplified``. This allows changes to the transform
        to propagate through the chain without requiring the chain to be
        re-simplified.
        """
        return self._dynamic

    @dynamic.setter
    def dynamic(self, d):
        self._dynamic = d

    def shader_map(self):
        """
        Return a shader Function that accepts only a single vec4 argument
        and defines new attributes / uniforms supplying the Function with
        any static input.
        """
        return self._shader_map

    def shader_imap(self):
        """See shader_map."""
        if self.inverse_kind is InverseKind.NONE:
            raise NotImplementedError(
                f"{type(self).__name__} does not provide an inverse transform"
            )
        return self._shader_imap

    def _shader_object(self):
        """This method allows transforms to be assigned directly to shader
        template variables. 

        Example::

            code = 'void main() { gl_Position = $transform($position); }'
            func = shaders.Function(code)
            tr = STTransform()
            func['transform'] = tr  # use tr's forward mapping for $function
        """
        return self.shader_map()

    def update(self, *args):
        """Called to inform any listeners that this transform has changed."""
        self.changed(*args)

    def __mul__(self, tr):
        """
        Transform multiplication returns a new transform that is equivalent to
        the two operands performed in series.

        By default, multiplying two Transforms `A * B` will return
        ChainTransform([A, B]). Subclasses may redefine this operation to
        return more optimized results.

        To ensure that both operands have a chance to simplify the operation,
        all subclasses should follow the same procedure. For `A * B`:

        1. A.__mul__(B) attempts to generate an optimized transform product.
        2. If that fails, it must:

               * return super(A).__mul__(B) OR
               * return NotImplemented if the superclass would return an
                 invalid result.

        3. When BaseTransform.__mul__(A, B) is called, it returns 
           NotImplemented, which causes B.__rmul__(A) to be invoked.
        4. B.__rmul__(A) attempts to generate an optimized transform product.
        5. If that fails, it must:

               * return super(B).__rmul__(A) OR
               * return ChainTransform([B, A]) if the superclass would return
                 an invalid result.

        6. When BaseTransform.__rmul__(B, A) is called, ChainTransform([A, B])
           is returned.
        """
        # switch to __rmul__ attempts.
        # Don't use the "return NotImplemted" trick, because that won't work if
        # self and tr are of the same type.
        return tr.__rmul__(self)

    def __rmul__(self, tr):
        return ChainTransform([tr, self])

    def __repr__(self):
        return "<%s at 0x%x>" % (self.__class__.__name__, id(self))

    def __del__(self):
        # we can remove ourselves from *all* events in this situation.
        self.changed.disconnect()


class InverseTransform(BaseTransform):
    def __init__(self, transform):
        BaseTransform.__init__(self)
        self._inverse = transform
        self.map = transform.imap
        self.imap = transform.map

    @property
    def Linear(self):
        return self._inverse.Linear

    @property
    def Orthogonal(self):
        return self._inverse.Orthogonal

    @property
    def NonScaling(self):
        return self._inverse.NonScaling

    @property
    def Isometric(self):
        return self._inverse.Isometric

    @property
    def shader_map(self):
        return self._inverse.shader_imap

    @property
    def shader_imap(self):
        return self._inverse.shader_map

    def __repr__(self):
        return ("<Inverse of %r>" % repr(self._inverse))


# import here to avoid import cycle; needed for BaseTransform.__mul__.
from .chain import ChainTransform  # noqa
