# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from abc import ABCMeta, abstractmethod

import numpy as np

from vispy.gloo import VertexBuffer
from ..shaders import Function


class BaseFilter(object):
    """Superclass for all filters."""

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
    vcode : str | Function | None
        Vertex shader code. If None, ``vhook`` and ``vpos`` will
        be ignored.
    vhook : {'pre', 'post'}
        Hook name to attach the vertex shader to.
    vpos : int
        Position in the hook to attach the vertex shader.
    fcode : str | Function | None
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
            self.vshader = Function(vcode) if isinstance(vcode, str) else vcode
            self._vexpr = self.vshader()
            self._vhook = vhook
            self._vpos = vpos
        else:
            self.vshader = None

        if fcode is not None:
            self.fshader = Function(fcode) if isinstance(fcode, str) else fcode
            self._fexpr = self.fshader()
            self._fhook = fhook
            self._fpos = fpos
        else:
            self.fshader = None

        self._attached = False

    @property
    def attached(self):
        return self._attached

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

        self._attached = True
        self._visual = visual

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

        self._attached = False
        self._visual = None


class PrimitivePickingFilter(Filter, metaclass=ABCMeta):
    """Abstract base class for Visual-specific filters to implement a
    primitive-picking mode.

    Subclasses must (and usually only need to) implement
    :py:meth:`_get_picking_ids`.
    """

    def __init__(self, fpos=9, *, discard_transparent=False):
        # fpos is set to 9 by default to put it near the end, but before the
        # default PickingFilter
        vfunc = Function("""\
            varying vec4 v_marker_picking_color;
            void prepare_marker_picking() {
                v_marker_picking_color = $ids;
            }
        """)
        ffunc = Function("""\
            varying vec4 v_marker_picking_color;
            void marker_picking_filter() {
                if ( $enabled != 1 ) {
                    return;
                }
                if ( $discard_transparent == 1 && gl_FragColor.a == 0.0 ) {
                    discard;
                }
                gl_FragColor = v_marker_picking_color;
            }
        """)

        self._id_colors = VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        vfunc['ids'] = self._id_colors
        self._n_primitives = 0
        super().__init__(vcode=vfunc, fcode=ffunc, fpos=fpos)
        self.enabled = False
        self.discard_transparent = discard_transparent

    @abstractmethod
    def _get_picking_ids(self):
        """Return a 1D array of picking IDs for the vertices in the visual.

        Generally, this method should be implemented to:
            1. Calculate the number of primitives in the visual (may be
            persisted in `self._n_primitives`).
            2. Calculate a range of picking ids for each primitive in the
            visual. IDs should start from 1, reserving 0 for the background. If
            primitives comprise multiple vertices (triangles), ids may need to
            be repeated.

        The return value should be an array of uint32 with shape
        (num_vertices,).

        If no change to the picking IDs is needed (for example, the number of
        primitives has not changed), this method should return `None`.
        """
        raise NotImplementedError(self)

    def _update_id_colors(self):
        """Calculate the colors encoding the picking IDs for the visual.

        For performance, this method will not update the id colors VertexBuffer
        if :py:meth:`_get_picking_ids` returns `None`.
        """
        # this should remain untouched
        ids = self._get_picking_ids()
        if ids is not None:
            id_colors = self._pack_ids_into_rgba(ids)
            self._id_colors.set_data(id_colors)

    @staticmethod
    def _pack_ids_into_rgba(ids):
        """Pack an array of uint32 primitive ids into float32 RGBA colors."""
        if ids.dtype != np.uint32:
            raise ValueError(f"ids must be uint32, got {ids.dtype}")

        return np.divide(
            ids.view(np.uint8).reshape(-1, 4),
            255,
            dtype=np.float32
        )

    def _on_data_updated(self, event=None):
        if not self.attached:
            return
        self._update_id_colors()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, e):
        self._enabled = bool(e)
        self.fshader['enabled'] = int(self._enabled)
        self._on_data_updated()

    @property
    def discard_transparent(self):
        return self._discard_transparent

    @discard_transparent.setter
    def discard_transparent(self, d):
        self._discard_transparent = bool(d)
        self.fshader['discard_transparent'] = int(self._discard_transparent)

    def _attach(self, visual):
        super()._attach(visual)
        visual.events.data_updated.connect(self._on_data_updated)
        self._on_data_updated()

    def _detach(self, visual):
        visual.events.data_updated.disconnect(self._on_data_updated)
        super()._detach(visual)
