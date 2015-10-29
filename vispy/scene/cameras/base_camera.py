# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ...util import keys
from ..node import Node
from ...visuals.transforms import (STTransform, MatrixTransform,
                                   NullTransform, TransformCache)


class BaseCamera(Node):
    """ Base camera class.

    The Camera describes the perspective from which a ViewBox views its
    subscene, and the way that user interaction affects that perspective.

    Most functionality is implemented in subclasses. This base class has
    no user interaction and causes the subscene to use the same coordinate
    system as the ViewBox.

    Parameters
    ----------
    interactive : bool
        Whether the camera processes mouse and keyboard events.
    flip : tuple of bools
        For each dimension, specify whether it is flipped.
    up : {'+z', '-z', '+y', '-y', '+x', '-x'}
        The direction that is considered up. Default '+z'. Not all
        camera's may support this (yet).
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """

    # These define the state of the camera
    _state_props = ()

    # The fractional zoom to apply for a single pixel of mouse motion
    zoom_factor = 0.007

    def __init__(self, interactive=True, flip=None, up='+z', parent=None,
                 name=None):
        super(BaseCamera, self).__init__(parent, name)

        # The viewbox for which this camera is active
        self._viewbox = None

        # Linked cameras
        self._linked_cameras = []
        self._linked_cameras_no_update = None

        # Variables related to transforms
        self.transform = NullTransform()
        self._pre_transform = None
        self._viewbox_tr = STTransform()  # correction for viewbox
        self._projection = MatrixTransform()
        self._transform_cache = TransformCache()

        # For internal use, to store event related information
        self._event_value = None

        # Flags
        self._resetting = False  # Avoid lots of updates during set_range
        self._key_events_bound = False  # Have we connected to key events
        self._set_range_args = None  # hold set_range() args

        # Limits set in reset (interesting region of the scene)
        self._xlim = None  # None is flag that no reset has been performed
        self._ylim = None
        self._zlim = None

        # Our default state to apply when resetting
        self._default_state = None

        # We initialize these parameters here, because we want these props
        # available in all cameras. Note that PanZoom does not use _center
        self._fov = 0.0
        self._center = None
        self._depth_value = 1e6  # bit+depth >= 24, otherwise should do 3e3

        # Set parameters. These are all not part of the "camera state"
        self.interactive = bool(interactive)
        self.flip = flip if (flip is not None) else (False, False, False)
        self.up = up

    @property
    def depth_value(self):
        """The depth value to use  in orthographic and perspective projection

        For orthographic projections, ``depth_value`` is the distance between
        the near and far clipping planes. For perspective projections, it is
        the ratio between the near and far clipping plane distances.

        GL has a fixed amount of precision in the depth buffer, and a fixed
        constant will not work for both a very large range and very high
        precision. This property provides the user a way to override
        the default value if necessary.
        """
        return self._depth_value

    @depth_value.setter
    def depth_value(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError('depth value must be positive')
        self._depth_value = value
        self.view_changed()

    def _depth_to_z(self, depth):
        """ Get the z-coord, given the depth value.
        """
        val = self.depth_value
        return val - depth * 2 * val

    def _viewbox_set(self, viewbox):
        """ Friend method of viewbox to register itself.
        """
        self._viewbox = viewbox
        # Connect
        viewbox.events.mouse_press.connect(self.viewbox_mouse_event)
        viewbox.events.mouse_release.connect(self.viewbox_mouse_event)
        viewbox.events.mouse_move.connect(self.viewbox_mouse_event)
        viewbox.events.mouse_wheel.connect(self.viewbox_mouse_event)
        viewbox.events.resize.connect(self.viewbox_resize_event)
        # todo: also add key events! (and also on viewbox (they're missing)

    def _viewbox_unset(self, viewbox):
        """ Friend method of viewbox to unregister itself.
        """
        self._viewbox = None
        # Disconnect
        viewbox.events.mouse_press.disconnect(self.viewbox_mouse_event)
        viewbox.events.mouse_release.disconnect(self.viewbox_mouse_event)
        viewbox.events.mouse_move.disconnect(self.viewbox_mouse_event)
        viewbox.events.mouse_wheel.disconnect(self.viewbox_mouse_event)
        viewbox.events.resize.disconnect(self.viewbox_resize_event)

    @property
    def viewbox(self):
        """ The viewbox that this camera applies to.
        """
        return self._viewbox

    ## Camera attributes

    @property
    def interactive(self):
        """ Boolean describing whether the camera should enable or disable
        user interaction.
        """
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        self._interactive = bool(value)

    @property
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, value):
        if not isinstance(value, (list, tuple)):
            raise ValueError('Flip must be a tuple or list.')
        if len(value) == 2:
            self._flip = bool(value[0]), bool(value[1]), False
        elif len(value) == 3:
            self._flip = bool(value[0]), bool(value[1]), bool(value[2])
        else:
            raise ValueError('Flip must have 2 or 3 elements.')
        self._flip_factors = tuple([(1-x*2) for x in self._flip])
        self.view_changed()

    @property
    def up(self):
        """ The dimension that is considered up.
        """
        return self._up

    @up.setter
    def up(self, value):
        value = value.lower()
        value = ('+' + value) if value in 'zyx' else value
        if value not in ('+z', '-z', '+y', '-y', '+x', '-x'):
            raise ValueError('Invalid value for up.')
        self._up = value
        self.view_changed()

    @property
    def center(self):
        """ The center location for this camera

        The exact meaning of this value differs per type of camera, but
        generally means the point of interest or the rotation point.
        """
        return self._center or (0, 0, 0)

    @center.setter
    def center(self, val):
        if len(val) == 2:
            self._center = float(val[0]), float(val[1]), 0.0
        elif len(val) == 3:
            self._center = float(val[0]), float(val[1]), float(val[2])
        else:
            raise ValueError('Center must be a 2 or 3 element tuple')
        self.view_changed()

    @property
    def fov(self):
        """ Field-of-view angle of the camera. If 0, the camera is in
        orthographic mode.
        """
        return self._fov

    @fov.setter
    def fov(self, fov):
        fov = float(fov)
        if fov < 0 or fov >= 180:
            raise ValueError("fov must be between 0 and 180.")
        self._fov = fov
        self.view_changed()

    ## Camera methods

    def set_range(self, x=None, y=None, z=None, margin=0.05):
        """ Set the range of the view region for the camera

        Parameters
        ----------
        x : tuple | None
            X range.
        y : tuple | None
            Y range.
        z : tuple | None
            Z range.
        margin : float
            Margin to use.

        Notes
        -----
        The view is set to the given range or to the scene boundaries
        if ranges are not specified. The ranges should be 2-element
        tuples specifying the min and max for each dimension.

        For the PanZoomCamera the view is fully defined by the range.
        For e.g. the TurntableCamera the elevation and azimuth are not
        set. One should use reset() for that.
        """
        # Flag to indicate that this is an initializing (not user-invoked)
        init = self._xlim is None

        # Collect given bounds
        bounds = [None, None, None]
        if x is not None:
            bounds[0] = float(x[0]), float(x[1])
        if y is not None:
            bounds[1] = float(y[0]), float(y[1])
        if z is not None:
            bounds[2] = float(z[0]), float(z[1])
        # If there is no viewbox, store given bounds in lim variables, and stop
        if self._viewbox is None:
            self._set_range_args = bounds[0], bounds[1], bounds[2], margin
            return

        # There is a viewbox, we're going to set the range for real
        self._resetting = True

        # Get bounds from viewbox if not given
        if all([(b is None) for b in bounds]):
            bounds = self._viewbox.get_scene_bounds()
        else:
            for i in range(3):
                if bounds[i] is None:
                    bounds[i] = self._viewbox.get_scene_bounds(i)
        
        # Calculate ranges and margins
        ranges = [b[1] - b[0] for b in bounds]
        margins = [(r*margin or 0.1) for r in ranges]
        # Assign limits for this camera
        bounds_margins = [(b[0]-m, b[1]+m) for b, m in zip(bounds, margins)]
        self._xlim, self._ylim, self._zlim = bounds_margins
        # Store center location
        if (not init) or (self._center is None):
            self._center = [(b[0] + r / 2) for b, r in zip(bounds, ranges)]

        # Let specific camera handle it
        self._set_range(init)

        # Finish
        self._resetting = False
        self.view_changed()

    def _set_range(self, init):
        pass

    def reset(self):
        """ Reset the view to the default state.
        """
        self.set_state(self._default_state)

    def set_default_state(self):
        """ Set the current state to be the default state to be applied
        when calling reset().
        """
        self._default_state = self.get_state()

    def get_state(self):
        """ Get the current view state of the camera

        Returns a dict of key-value pairs. The exact keys depend on the
        camera. Can be passed to set_state() (of this or another camera
        of the same type) to reproduce the state.
        """
        D = {}
        for key in self._state_props:
            D[key] = getattr(self, key)
        return D

    def set_state(self, state=None, **kwargs):
        """ Set the view state of the camera

        Should be a dict (or kwargs) as returned by get_state. It can
        be an incomlete dict, in which case only the specified
        properties are set.

        Parameters
        ----------
        state : dict
            The camera state.
        **kwargs : dict
            Unused keyword arguments.
        """
        D = state or {}
        D.update(kwargs)
        for key, val in D.items():
            if key not in self._state_props:
                raise KeyError('Not a valid camera state property %r' % key)
            setattr(self, key, val)

    def link(self, camera):
        """ Link this camera with another camera of the same type

        Linked camera's keep each-others' state in sync.

        Parameters
        ----------
        camera : instance of Camera
            The other camera to link.
        """
        cam1, cam2 = self, camera
        # Remove if already linked
        while cam1 in cam2._linked_cameras:
            cam2._linked_cameras.remove(cam1)
        while cam2 in cam1._linked_cameras:
            cam1._linked_cameras.remove(cam2)
        # Link both ways
        cam1._linked_cameras.append(cam2)
        cam2._linked_cameras.append(cam1)

    ## Event-related methods

    def view_changed(self):
        """ Called when this camera is changes its view. Also called
        when its associated with a viewbox.
        """
        if self._resetting:
            return  # don't update anything while resetting (are in set_range)
        if self._viewbox:
            # Set range if necessary
            if self._xlim is None:
                args = self._set_range_args or ()
                self.set_range(*args)
            # Store default state if we have not set it yet
            if self._default_state is None:
                self.set_default_state()
            # Do the actual update
            self._update_transform()

    @property
    def pre_transform(self):
        """ A transform to apply to the beginning of the scene transform, in
        addition to anything else provided by this Camera.
        """
        return self._pre_transform

    @pre_transform.setter
    def pre_transform(self, tr):
        self._pre_transform = tr
        self.view_changed()

    def viewbox_mouse_event(self, event):
        """Viewbox mouse event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        pass

    def on_canvas_change(self, event):
        """Canvas change event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        # Connect key events from canvas to camera. 
        # TODO: canvas should keep track of a single node with keyboard focus.
        if event.old is not None:
            event.old.events.key_press.disconnect(self.viewbox_key_event)
            event.old.events.key_release.disconnect(self.viewbox_key_event)
        if event.new is not None:
            event.new.events.key_press.connect(self.viewbox_key_event)
            event.new.events.key_release.connect(self.viewbox_key_event)

    def viewbox_key_event(self, event):
        """ViewBox key event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        if event.key == keys.BACKSPACE:
            self.reset()

    def viewbox_resize_event(self, event):
        """The ViewBox resize handler to update the transform

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        pass

    def _update_transform(self):
        """ Subclasses should reimplement this method to update the scene
        transform by calling self._set_scene_transform.
        """
        self._set_scene_transform(self.transform)

    def _set_scene_transform(self, tr):
        """ Called by subclasses to configure the viewbox scene transform.
        """
        # todo: check whether transform has changed, connect to
        # transform.changed event
        pre_tr = self.pre_transform
        if pre_tr is None:
            self._scene_transform = tr
        else:
            self._transform_cache.roll()
            self._scene_transform = self._transform_cache.get([pre_tr, tr])

        # Mark the transform dynamic so that it will not be collapsed with
        # others 
        self._scene_transform.dynamic = True
        
        # Update scene
        self._viewbox.scene.transform = self._scene_transform
        self._viewbox.update()

        # Apply same state to linked cameras, but prevent that camera
        # to return the favor
        for cam in self._linked_cameras:
            if cam is self._linked_cameras_no_update:
                continue
            try:
                cam._linked_cameras_no_update = self
                cam.set_state(self.get_state())
            finally:
                cam._linked_cameras_no_update = None
