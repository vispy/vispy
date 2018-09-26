# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


from ..shaders import Function


class BaseFilter(object):
    """Base class for all filters.
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
    def __new__(cls, name, bases, attrs):
        try:
            __slots__ = list(attrs['__slots__'])
        except KeyError:
            __slots__ = []

        if 'fshader' in __slots__:
            raise TypeError("cannot pre-define 'fshader' in %s.__slots__"
                            % name)
        if 'vshader' in __slots__:
            raise TypeError("cannot pre-define 'vshader' in %s.__slots__"
                            % name)

        has_fshader = False
        has_vshader = False

        if attrs.get('FRAG_SHADER'):
            if not attrs.get('FRAG_HOOK'):
                raise ValueError('If FRAG_SHADER is defined, '
                                 '%s must also define FRAG_HOOK.' % name)
            has_fshader = True

        if attrs.get('VERT_SHADER'):
            if not attrs.get('VERT_HOOK'):
                raise ValueError('If FRAG_SHADER is defined, '
                                 '%s must also define FRAG_HOOK.' % name)
            has_vshader = True

        if not has_fshader and not has_vshader:
            if Filter is not None:  # if we are not creating Filter itself
                raise ValueError('%s must define either FRAG_SHADER or '
                                 'VERT_SHADER.' % name)

        if has_vshader:
            __slots__.insert(0, 'vshader_expr')
            __slots__.insert(0, 'vshader')
        if has_fshader:
            __slots__.insert(0, 'fshader_expr')
            __slots__.insert(0, 'fshader')

        attrs['__slots__'] = tuple(__slots__)
        return type.__new__(cls, name, bases, attrs)


class Filter(BaseFilter, metaclass=FilterMeta):
    def __new__(self):
        if hasattr(self, 'FRAG_SHADER'):
            self.fshader = Function(self.FRAG_SHADER)
            self.fshader_expr = self.fshader()
        if hasattr(self, 'VERT_SHADER'):
            self.vshader = Function(self.VERT_SHADER)
            self.vshader_expr = self.vshader()

    def _attach(self, visual):
        """Called when a filter should be attached to a visual.

        Parameters
        ----------
        visual : instance of Visual
            The visual that called this.
        """
        if hasattr(self, 'FRAG_SHADER'):
            hook = visual._get_hook(self.FRAG_SHADER, self.FRAG_HOOK)
            try:
                hook.add(self.fshader_expr, position=self.FRAG_POSITION)
            except AttributeError:
                hook.add(self.fshader_expr)
        if hasattr(self, 'VERT_SHADER'):
            hook = visual._get_hook(self.VERT_SHADER, self.VERT_HOOK)
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
            hook = visual._get_hook(self.FRAG_SHADER, self.FRAG_HOOK)
            hook.remove(self.fshader_expr)
        if hasattr(self, 'VERT_SHADER'):
            hook = visual._get_hook(self.VERT_SHADER, self.VERT_HOOK)
            hook.remove(self.vshader_expr)
