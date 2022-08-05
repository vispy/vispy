# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
from typing import Union

import numpy as np

from .widget import Widget
from ..subscene import SubScene
from ..cameras import make_camera, BaseCamera
from ...visuals.filters import Clipper


class ViewBox(Widget):
    """Provides a rectangular widget to which its subscene is rendered.

    Three classes work together when using a ViewBox:
    * The :class:`SubScene` class describes a "world" coordinate system and the
    entities that live inside it.
    * ViewBox is a "window" through which we view the
    subscene. Multiple ViewBoxes may view the same subscene.
    * :class:`Camera` describes both the perspective from which the
    subscene is rendered, and the way user interaction affects that
    perspective.

    In general it is only necessary to create the ViewBox; a SubScene and
    Camera will be generated automatically.

    Parameters
    ----------
    camera : instance of Camera | str | None
        The camera through which to view the SubScene. If None, then a
        PanZoomCamera (2D interaction) is used. If str, then the string is
        used as the argument to :func:`make_camera`.
    **kwargs : dict
        Extra keyword arguments to pass to `Widget`.
    """

    def __init__(self, camera=None, **kwargs):
        self._camera = None
        self._scene = None
        Widget.__init__(self, **kwargs)
        self.interactive = True

        # Each viewbox has an internal scene node, which has a transform that
        # represents the transformation imposed by camera.
        if self.name is not None:
            name = str(self.name) + "_Scene"
        else:
            name = None

        self._scene = SubScene(name=name, parent=self)
        self._scene._clipper = Clipper()
        self._scene.clip_children = True
        self.transforms.changed.connect(self._update_scene_clipper)

        # Camera is a helper object that handles scene transformation
        # and user interaction.
        if camera is None:
            camera = 'base'
        if isinstance(camera, str):
            self.camera = make_camera(camera, parent=self.scene)
        elif isinstance(camera, BaseCamera):
            self.camera = camera
        else:
            raise TypeError('Argument "camera" must be None, str, or Camera.')

    @property
    def camera(self) -> BaseCamera:
        """Get/set the Camera in use by this ViewBox

        If a string is given (e.g. 'panzoom', 'turntable', 'fly'). A
        corresponding camera is selected if it already exists in the
        scene, otherwise a new camera is created.

        The camera object is made a child of the scene (if it is not
        already in the scene).

        Multiple cameras can exist in one scene, although only one can
        be active at a time. A single camera can be used by multiple
        viewboxes at the same time.
        """
        return self._camera

    @camera.setter
    def camera(self, cam: Union[str, BaseCamera]):
        if isinstance(cam, str):
            # Try to select an existing camera
            for child in self.scene.children:
                if isinstance(child, BaseCamera):
                    this_cam_type = child.__class__.__name__.lower()[:-6]
                    if this_cam_type == cam:
                        self.camera = child
                        return
            else:
                # No such camera yet, create it then
                self.camera = make_camera(cam)

        elif isinstance(cam, BaseCamera):
            # Ensure that the camera is in the scene
            if not self.is_in_scene(cam):
                cam.parent = self.scene
            # Disconnect / connect
            if self._camera is not None:
                self._camera._viewbox_unset(self)
            self._camera = cam
            if self._camera is not None:
                self._camera._viewbox_set(self)
            # Update view
            cam.view_changed()

        else:
            raise ValueError('Not a camera object.')

    def is_in_scene(self, node):
        """Get whether the given node is inside the scene of this viewbox.

        Parameters
        ----------
        node : instance of Node
            The node.
        """
        return self.scene.is_child(node)

    def get_scene_bounds(self, dim=None):
        """Get the total bounds based on the visuals present in the scene

        Parameters
        ----------
        dim : int | None
            Dimension to return.

        Returns
        -------
        bounds : list | tuple
            If ``dim is None``, Returns a list of 3 tuples, otherwise
            the bounds for the requested dimension.
        """
        # todo: handle sub-children
        # todo: handle transformations
        # Init
        bounds = [(np.inf, -np.inf), (np.inf, -np.inf), (np.inf, -np.inf)]
        # Get bounds of all children
        for ob in self.scene.children:
            if hasattr(ob, 'bounds'):
                for axis in (0, 1, 2):
                    if (dim is not None) and dim != axis:
                        continue
                    b = ob.bounds(axis)
                    if b is not None:
                        b = min(b), max(b)  # Ensure correct order
                        bounds[axis] = (min(bounds[axis][0], b[0]),
                                        max(bounds[axis][1], b[1]))
        # Set defaults
        for axis in (0, 1, 2):
            if any(np.isinf(bounds[axis])):
                bounds[axis] = -1, 1

        if dim is not None:
            return bounds[dim]
        else:
            return bounds

    @property
    def scene(self):
        """The root node of the scene viewed by this ViewBox."""
        return self._scene

    def add(self, node):
        """Add an Node to the scene for this ViewBox.

        This is a convenience method equivalent to
        `node.parent = viewbox.scene`

        Parameters
        ----------
        node : instance of Node
            The node to add.
        """
        node.parent = self.scene

    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        if self._scene is None:
            # happens during init
            return
        self._update_scene_clipper()

    def _update_scene_clipper(self, event=None):
        tr = self.get_transform('visual', 'framebuffer')
        self._scene._clipper.bounds = tr.map(self.inner_rect)
