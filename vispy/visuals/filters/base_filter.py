# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import six
from warnings import warn

from ..shaders import Function


class BaseFilter(object):
    """Superclass for all filters.
    """
    def _attach(self, visual):
        """Called when a filter should be attached to a visual.

        Parameters
        ----------
        visual : instance of BaseVisual
            The visual that called this.
        """
        raise NotImplementedError(self)

    def _detach(self, visual):
        """Called when a filter should be detached from a visual.

        Parameters
        ----------
        visual : instance of BaseVisual
            The visual that called this.
        """
        raise NotImplementedError(self)


Filter = None  # allows to be called in metaclass before created


class FilterMeta(type):
    """Metaclass for management of Filter subclasses.

    Checks that at least one of the class attributes FRAG_SHADER
    or VERT_SHADER are defined along with the corresponding hook
    name (usually 'pre' or 'post') as FRAG_HOOK and VERT_HOOK.

    These required attributes may be inherited.
    """
    def __new__(cls, name, bases, attrs):
        has_fshader = False
        has_vshader = False

        def class_has_attr(name):
            """Whether cls has defined or inherited an attribute.
            """
            if name in attrs:
                return True
            for base in bases:
                if hasattr(base, name):
                    return True
            return False

        if class_has_attr('FRAG_SHADER'):
            if not class_has_attr('FRAG_HOOK'):
                raise ValueError('If FRAG_SHADER is defined, '
                                 '%s must also define FRAG_HOOK.' % name)
            has_fshader = True

        if class_has_attr('VERT_SHADER'):
            if not class_has_attr('VERT_HOOK'):
                raise ValueError('If VERT_SHADER is defined, '
                                 '%s must also define VERT_HOOK.' % name)
            has_vshader = True

        if not has_fshader and class_has_attr('FRAG_POSITION'):
            warn('%s inherits or defines FRAG_POSITION when no '
                 ' FRAG_SHADER set.' % name)

        if not has_vshader and class_has_attr('VERT_POSITION'):
            warn('%s inherits or defines VERT_POSITION when no '
                 ' VERT_SHADER set.' % name)

        if not has_fshader and not has_vshader:
            if Filter is not None:  # if we are not creating Filter itself
                raise ValueError('%s must define either FRAG_SHADER or '
                                 'VERT_SHADER.' % name)

        return type.__new__(cls, name, bases, attrs)


class Filter(six.with_metaclass(FilterMeta, BaseFilter)):
    """Base class for all filters that use fragment and/or vertex shaders.

    All subclasses must define or inherit from a class that defines
    FRAG_SHADER and/or VERT_SHADER program code as class attributes
    in addition to FRAG_HOOK and/or VERT_HOOK, respectively. Hook
    names are typically 'pre' or 'post'.

    Optionally, the position in which programs are slotted can
    be specified by the FRAG_POSITION and VERT_POSITION class attributes.

    Attributes for the program are automatically created as
    fshader (Function) and fshader_expr (FunctionCall) for fragment shaders
    and vshader (Function) and vshader_expr (FunctionCall) for vertex shaders.
    """
    def __new__(cls, *args, **kwargs):
        self = super(Filter, cls).__new__(cls)

        if hasattr(cls, 'FRAG_SHADER'):
            self.fshader = Function(self.FRAG_SHADER)
            self.fshader_expr = self.fshader()

        if hasattr(cls, 'VERT_SHADER'):
            self.vshader = Function(self.VERT_SHADER)
            self.vshader_expr = self.vshader()

        return self

    def _attach(self, visual):
        """Called when a filter should be attached to a visual.

        Parameters
        ----------
        visual : instance of Visual
            The visual that called this.
        """
        if hasattr(self, 'FRAG_SHADER'):
            hook = visual._get_hook('frag', self.FRAG_HOOK)
            try:
                hook.add(self.fshader_expr, position=self.FRAG_POSITION)
            except AttributeError:
                hook.add(self.fshader_expr)

        if hasattr(self, 'VERT_SHADER'):
            hook = visual._get_hook('vert', self.VERT_HOOK)
            try:
                hook.add(self.vshader_expr, position=self.VERT_POSITION)
            except AttributeError:
                hook.add(self.vshader_expr)

    def _detach(self, visual):
        """Called when a filter should be detached from a visual.

        Parameters
        ----------
        visual : instance of Visual
            The visual that called this.
        """
        if hasattr(self, 'FRAG_SHADER'):
            hook = visual._get_hook('frag', self.FRAG_HOOK)
            hook.remove(self.fshader_expr)

        if hasattr(self, 'VERT_SHADER'):
            hook = visual._get_hook('vert', self.VERT_HOOK)
            hook.remove(self.vshader_expr)
