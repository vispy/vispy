# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

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


class Filter(BaseFilter):
    """Base class for all filters that use fragment and/or vertex shaders.

    Parameters
    ----------
    vcode : str | None
        Vertex shader code. If None, ``vhook`` and ``vpos`` will
        be ignored.
    vhook : {'pre', 'post'}
        Hook name to attach the vertex shader to.
    vpos : int
        Position in the hook to attach the vertex shader.
    fcode : str | None
        Fragment shader code. If None, ``fhook`` and ``fpos`` will
        be ignored.
    fhook : {'pre', 'post'}
        Hook name to attach the fragment shader to.
    fpos : int
        Position in the hook to attach the fragment shader.

    Attributes
    ----------
    vshader : Function | None
        Vertex shader.
    fshader : Function | None
        Fragment shader.
    """
    def __init__(self, vcode=None, vhook='post', vpos=5,
                 fcode=None, fhook='post', fpos=5):
        super(Filter, self).__init__()

        if vcode is not None:
            self.vshader = Function(vcode)
            self._vexpr = self.vshader()
            self._vhook = vhook
            self._vpos = vpos
        else:
            self.vshader = None

        if fcode is not None:
            self.fshader = Function(fcode)
            self._fexpr = self.fshader()
            self._fhook = fhook
            self._fpos = fpos
        else:
            self.fshader = None

    def _attach(self, visual):
        """Called when a filter should be attached to a visual.

        Parameters
        ----------
        visual : instance of Visual
            The visual that called this.
        """
        if self.vshader:
            hook = visual._get_hook('vert', self._vhook)
            hook.add(self._vexpr, position=self._vpos)

        if self.fshader:
            hook = visual._get_hook('frag', self._fhook)
            hook.add(self._fexpr, position=self._fpos)

    def _detach(self, visual):
        """Called when a filter should be detached from a visual.

        Parameters
        ----------
        visual : instance of Visual
            The visual that called this.
        """
        if self.vshader:
            hook = visual._get_hook('vert', self._vhook)
            hook.remove(self._vexpr)

        if self.fshader:
            hook = visual._get_hook('frag', self._fhook)
            hook.remove(self._fexpr)
