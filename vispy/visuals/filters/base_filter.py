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
    :py:meth:`_update_id_colors`.
    """

    def __init__(self, fpos=9):
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
                if ($enabled != 1) {
                    return;
                }
                gl_FragColor = v_marker_picking_color;
            }
        """)

        self._id_colors = VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        vfunc['ids'] = self._id_colors
        self._n_primitives = 0
        # set fpos to a very big number to make sure this is applied last
        super().__init__(vcode=vfunc, fcode=ffunc, fpos=1e9)
        self.enabled = False

    @abstractmethod
    def _update_id_colors(self):
        """Calculate the colors encoding the picking IDs for the visual.

        Generally, this method should be implemented to:
            1. Calculate the number of primitives in the visual, stored in
            `self._n_primitives`.
            2. Pack the picking IDs into a 4-component float array (RGBA
            VertexBuffer), stored in `self._id_colors`.

        As an example of packing IDs into a VertexBuffer, consider the following
        implementation for the Mesh visual:
        ```
            # calculate the number of primitives
            n_faces = len(self._visual.mesh_data.get_faces())
            self._n_primitives = n_faces

            # assign 32 bit IDs to each primitive
            # starting from 1 reserves (0, 0, 0, 0) for the background
            ids = np.arange(1, n_faces + 1,dtype=np.uint32)

            # reinterpret as 8-bit RGBA and normalize colors into floats
            id_colors = np.divide(
                ids.view(np.uint8).reshape(n_faces, 4),
                255,
                dtype=np.float32
            )

            # store the colors in a VertexBuffer, repeating each color 3 times
            # for each vertex in each triangle
            self._id_colors.set_data(np.repeat(idid_colors, 3, axis=0))
        ```

        For performance, you may want to optimize this method to only update
        the IDs when the data meaningfully changes - for example when the
        number of primitives changes.
        """
        raise NotImplementedError(self)

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

    def _attach(self, visual):
        super()._attach(visual)
        visual.events.data_updated.connect(self._on_data_updated)
        self._on_data_updated()

    def _detach(self, visual):
        visual.events.data_updated.disconnect(self._on_data_updated)
        super()._detach(visual)
