# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..shaders import Function
from ...util.event import EventEmitter

"""
API Issues to work out:

  - AffineTransform and STTransform both have 'scale' and 'translate'
    attributes, but they are used in very different ways. It would be nice
    to keep this consistent, but how?

  - Need a transform.map_rect function that returns the bounding rectangle of
    a rect after transformation. Non-linear transforms might need to work
    harder at this, but we can provide a default implementation that
    works by mapping a selection of points across a grid within the original
    rect.
"""


class BaseTransform(object):
    """
    BaseTransform is a base class that defines a pair of complementary
    coordinate mapping functions in both python and GLSL.

    All BaseTransform subclasses define map() and imap() methods that map
    an object through the forward or inverse transformation, respectively.

    The two class variables glsl_map and glsl_imap are instances of
    shaders.Function that define the forward- and inverse-mapping GLSL
    function code.

    Optionally, an inverse() method returns a new transform performing the
    inverse mapping.

    Note that although all classes should define both map() and imap(), it
    is not necessarily the case that imap(map(x)) == x; there may be instances
    where the inverse mapping is ambiguous or otherwise meaningless.

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

    def __init__(self):
        self._inverse = None
        self.changed = EventEmitter(source=self, type='transform_changed')
        if self.glsl_map is not None:
            self._shader_map = Function(self.glsl_map)
        if self.glsl_imap is not None:
            self._shader_imap = Function(self.glsl_imap)

    def map(self, obj):
        """
        Return *obj* mapped through the forward transformation.

        Parameters:
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        raise NotImplementedError()

    def imap(self, obj):
        """
        Return *obj* mapped through the inverse transformation.

        Parameters:
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        raise NotImplementedError()

    @property
    def inverse(self):
        """ The inverse of this transform. 
        """
        if self._inverse is None:
            self._inverse = InverseTransform(self)
        return self._inverse

    def shader_map(self):
        """
        Return a shader Function that accepts only a single vec4 argument
        and defines new attributes / uniforms supplying the Function with
        any static input.
        """
        return self._shader_map

    def shader_imap(self):
        """
        see shader_map.
        """
        return self._shader_imap

    def update(self):
        """
        Called to inform any listeners that this transform has changed.
        """
        self.changed()

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


class InverseTransform(BaseTransform):
    def __init__(self, transform):
        self._transform = transform
        self.shader_map = self._transform.shader_imap
        self.shader_imap = self._transform.shader_map
        self.map = self._transform.imap
        self.imap = self._transform.map
        
    @property
    def inverse(self):
        return self._transform
    
    def __repr__(self):
        return ("<Inverse of %r>" % repr(self._transform))
        

# import here to avoid import cycle; needed for BaseTransform.__mul__.
from .chain import ChainTransform
