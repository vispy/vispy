# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import math

import numpy as np

from ...app import Timer
from ...util.quaternion import Quaternion
from ...util import keys
from ..node import Node
from ...geometry import Rect
from ...visuals.transforms import (STTransform, PerspectiveTransform,
                                   NullTransform, AffineTransform,
                                   TransformCache)


# todo: Make 3D cameras use same internal state: less code, smooth transitions


def make_camera(cam_type, *args, **kwargs):
    """ Factory function for creating new cameras using a string name.

    Parameters
    ----------
    cam_type : str
        May be one of:
            * 'panzoom' : Creates :class:`PanZoomCamera`
            * 'turntable' : Creates :class:`TurntableCamera`
            * None : Creates :class:`Camera`

    All extra arguments are passed to the __init__ method of the selected
    Camera class.
    """
    cam_types = {None: BaseCamera}
    for camType in (BaseCamera, PanZoomCamera, PerspectiveCamera,
                    TurntableCamera, FlyCamera, ArcballCamera):
        cam_types[camType.__name__[:-6].lower()] = camType

    try:
        return cam_types[cam_type](*args, **kwargs)
    except KeyError:
        raise KeyError('Unknown camera type "%s". Options are: %s' %
                       (cam_type, cam_types.keys()))


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

    def __init__(self, interactive=True, flip=None, up='+z', **kwargs):
        super(BaseCamera, self).__init__(**kwargs)

        # The viewbox for which this camera is active
        self._viewbox = None

        # Linked cameras
        self._linked_cameras = []
        self._linked_cameras_no_update = False  # internal flag

        # Variables related to transforms
        self.transform = NullTransform()
        self._pre_transform = None
        self._viewbox_tr = STTransform()  # correction for viewbox
        self._projection = PerspectiveTransform()
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

        # Set parameters. These are all not part of the "camera state"
        self.interactive = bool(interactive)
        self.flip = flip if (flip is not None) else (False, False, False)
        self.up = up

    def _get_depth_value(self):
        """ Get the depth value to use in orthographic and perspective projection

        For 24 bits and more, we're fine with 100.000, but for 16 bits we
        need 3000 or so. The criterion is that at the center, we should be
        able to distinguish between 0.1, 0.0 and -0.1 etc.
        """
        if True:  # bit+depth >= 24
            return 100000.0
        else:
            return 3000.0

    def _depth_to_z(self, depth):
        """ Get the z-coord, given the depth value.
        """
        val = self._get_depth_value()
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
        # todo: connect this method to viewbox.events.key_down
        # viewbox does not currently support key events
        # A bit awkward way to connect to our canvas; we need event
        # object to get a reference to the canvas
        # todo: fix this, also only receive key events when over the viewbox
        if not self._key_events_bound:
            self._key_events_bound = True
            event.canvas.events.key_press.connect(self.viewbox_key_event)
            event.canvas.events.key_release.connect(self.viewbox_key_event)

    def viewbox_key_event(self, event):
        if event.key == keys.BACKSPACE:
            self.reset()

    def viewbox_resize_event(self, event):
        """
        The ViewBox was resized; update the transform accordingly.
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

        # Update scene
        self._viewbox.scene.transform = self._scene_transform
        self._viewbox.update()

        # Apply same state to linked cameras, but prevent that camera
        # to return the favor
        if not self._linked_cameras_no_update:
            for cam in self._linked_cameras:
                cam._linked_cameras_no_update = True
                try:
                    cam.set_state(self.get_state())
                finally:
                    cam._linked_cameras_no_update = False


class PanZoomCamera(BaseCamera):
    """ Camera implementing 2D pan/zoom mouse interaction.

    For this camera, the ``scale_factor`` indicates the zoom level, and
    the ``center`` indicates the center position of the view.

    By default, this camera inverts the y axis of the scene. This usually
    results in the scene +y axis pointing upward because widgets (including
    ViewBox) have their +y axis pointing downward.

    Parameters
    ----------
    rect : Rect
        A Rect object or 4-element tuple that specifies the rectangular
        area to show.
    aspect : float | None
        The aspect ratio (i.e. scaling) between x and y dimension of
        the scene. E.g. to show a square image as square, the aspect
        should be 1. If None (default) the x and y dimensions are scaled
        independently.
    See BaseCamera for more.

    Interaction
    -----------
    * LMB: pan the view
    * RMB or scroll: zooms the view

    """

    _state_props = BaseCamera._state_props + ('rect', )

    def __init__(self, rect=None, aspect=None, **kwargs):
        super(PanZoomCamera, self).__init__(**kwargs)

        self.transform = STTransform()

        # Set camera attributes
        self.aspect = aspect
        self._rect = None
        if rect is not None:
            self.rect = rect

    @property
    def aspect(self):
        """ The ratio between the x and y dimension. E.g. to show a
        square image as square, the aspect should be 1. If None, the
        dimensions are scaled automatically, dependening on the
        available space. Otherwise the ratio between the dimensions
        is fixed.
        """
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        if value is None:
            self._aspect = None
        else:
            self._aspect = float(value)
        self.view_changed()

    def zoom(self, factor, center=None):
        """ Zoom in (or out) at the given center

        Parameters
        ----------
        factor : float or tuple
            Fraction by which the scene should be zoomed (e.g. a factor of 2
            causes the scene to appear twice as large).
        center : tuple of 2-4 elements
            The center of the view. If not given or None, use the
            current center.
        """
        assert len(center) in (2, 3, 4)
        
        # Get scale factor, take scale ratio into account
        if np.isscalar(factor):
            scale = [factor, factor]
        else:
            if len(factor) != 2:
                raise TypeError("factor must be scalar or length-2 sequence.")
            scale = list(factor)
        if self.aspect is not None:
            scale[0] = scale[1]
        
        # Init some variables
        center = center if (center is not None) else self.center
        rect = self.rect
        # Get space from given center to edges
        left_space = center[0] - rect.left
        right_space = rect.right - center[0]
        bottom_space = center[1] - rect.bottom
        top_space = rect.top - center[1]
        # Scale these spaces
        rect.left = center[0] - left_space * scale[0]
        rect.right = center[0] + right_space * scale[0]
        rect.bottom = center[1] - bottom_space * scale[1]
        rect.top = center[1] + top_space * scale[1]

        self.rect = rect

    def pan(self, *pan):
        """ Pan the view.

        Parameters
        ----------
        pan : length-2 sequence
            The distance to pan the view, in the coordinate system of the
            scene.
        """
        if len(pan) == 1:
            pan = pan[0]
        self.rect = self.rect + pan

    @property
    def rect(self):
        """ The rectangular border of the ViewBox visible area, expressed in
        the coordinate system of the scene.

        Note that the rectangle can have negative width or height, in
        which case the corresponding dimension is flipped (this flipping
        is independent from the camera's ``flip`` property).
        """
        return self._rect

    @rect.setter
    def rect(self, args):
        if isinstance(args, tuple):
            self._rect = Rect(*args)
        else:
            self._rect = Rect(args)
        self.view_changed()

    @property
    def center(self):
        rect = self._rect
        return 0.5 * (rect.left+rect.right), 0.5 * (rect.top+rect.bottom), 0

    @center.setter
    def center(self, center):
        if not (isinstance(center, (tuple, list)) and len(center) in (2, 3)):
            raise ValueError('center must be a 2 or 3 element tuple')
        rect = self.rect or Rect(0, 0, 1, 1)
        # Get half-ranges
        x2 = 0.5 * (rect.right - rect.left)
        y2 = 0.5 * (rect.top - rect.bottom)
        # Apply new ranges
        rect.left = center[0] - x2
        rect.right = center[0] + x2
        rect.bottom = center[1] - y2
        rect.top = center[1] + y2
        #
        self.rect = rect

    def _set_range(self, init):
        if init and self._rect is not None:
            return
        # Convert limits to rect
        w = self._xlim[1] - self._xlim[0]
        h = self._ylim[1] - self._ylim[0]
        self.rect = self._xlim[0], self._ylim[0], w, h

    def viewbox_resize_event(self, event):
        """ Modify the data aspect and scale factor, to adjust to
        the new window size.
        """
        self.view_changed()

    def viewbox_mouse_event(self, event):
        """
        The SubScene received a mouse event; update transform
        accordingly.
        """
        if event.handled or not self.interactive:
            return

        # Scrolling
        BaseCamera.viewbox_mouse_event(self, event)

        if event.type == 'mouse_wheel':
            center = self._scene_transform.imap(event.pos)
            self.zoom((1 + self.zoom_factor) ** (-event.delta[1] * 30), center)

        elif event.type == 'mouse_move':
            if event.press_event is None:
                return

            modifiers = event.mouse_event.modifiers
            p1 = event.mouse_event.press_event.pos
            p2 = event.mouse_event.pos

            if 1 in event.buttons and not modifiers:
                # Translate
                p1 = np.array(event.last_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1s = self._transform.imap(p1)
                p2s = self._transform.imap(p2)
                self.pan(p1s-p2s)

            elif 2 in event.buttons and not modifiers:
                # Zoom
                p1c = np.array(event.last_event.pos)[:2]
                p2c = np.array(event.pos)[:2]
                scale = ((1 + self.zoom_factor) ** 
                         ((p1c-p2c) * np.array([1, -1])))
                center = self._transform.imap(event.press_event.pos[:2])
                self.zoom(scale, center)

    def _update_transform(self):

        rect = self.rect
        self._real_rect = Rect(rect)
        vbr = self._viewbox.rect.flipped(x=self.flip[0], y=(not self.flip[1]))
        d = self._get_depth_value()

        # apply scale ratio constraint
        if self._aspect is not None:
            # Aspect ratio of the requested range
            requested_aspect = (rect.width / rect.height
                                if rect.height != 0 else 1)
            # Aspect ratio of the viewbox
            view_aspect = vbr.width / vbr.height if vbr.height != 0 else 1
            # View aspect ratio needed to obey the scale constraint
            constrained_aspect = abs(view_aspect / self._aspect)

            if requested_aspect > constrained_aspect:
                # view range needs to be taller than requested
                dy = 0.5 * (rect.width / constrained_aspect - rect.height)
                self._real_rect.top += dy
                self._real_rect.bottom -= dy
            else:
                # view range needs to be wider than requested
                dx = 0.5 * (rect.height * constrained_aspect - rect.width)
                self._real_rect.left -= dx
                self._real_rect.right += dx

        # Apply mapping between viewbox and cam view
        self.transform.set_mapping(self._real_rect, vbr)
        # Scale z, so that the clipping planes are between -alot and +alot
        self.transform.zoom((1, 1, 1/d))

        # We've now set self.transform, which represents our 2D
        # transform When up is +z this is all. In other cases,
        # self.transform is now set up correctly to allow pan/zoom, but
        # for the scene we need a different (3D) mapping. When there
        # is a minus in up, we simply look at the scene from the other
        # side (as if z was flipped).

        if self.up == '+z':
            thetransform = self.transform
        else:
            rr = self._real_rect
            tr = AffineTransform()
            d = d if (self.up[0] == '+') else -d
            pp1 = [(vbr.left, vbr.bottom, 0), (vbr.left, vbr.top, 0),
                   (vbr.right, vbr.bottom, 0), (vbr.left, vbr.bottom, 1)]
            # Get Mapping
            if self.up[1] == 'z':
                pp2 = [(rr.left, rr.bottom, 0), (rr.left, rr.top, 0),
                       (rr.right, rr.bottom, 0), (rr.left, rr.bottom, d)]
            elif self.up[1] == 'y':
                pp2 = [(rr.left, 0, rr.bottom), (rr.left, 0, rr.top),
                       (rr.right, 0, rr.bottom), (rr.left, d, rr.bottom)]
            elif self.up[1] == 'x':
                pp2 = [(0, rr.left, rr.bottom), (0, rr.left, rr.top),
                       (0, rr.right, rr.bottom), (d, rr.left, rr.bottom)]
            # Apply
            tr.set_mapping(np.array(pp2), np.array(pp1))
            thetransform = tr

        # Set on viewbox
        self._set_scene_transform(thetransform)


class PerspectiveCamera(BaseCamera):
    """ Base class for 3D cameras supporting orthographic and
    perspective projections.

    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    scale_factor : scalar
        A measure for the scale/range of the scene that the camera
        should show. The exact meaning differs per camera type.
    See BaseCamera for more.

    """

    _state_props = ('scale_factor', 'center', 'fov')

    def __init__(self, fov=60.0, scale_factor=None, center=None, **kwargs):
        super(PerspectiveCamera, self).__init__(**kwargs)
        # Camera transform
        self.transform = AffineTransform()

        # Set camera attributes
        self.fov = fov
        self._scale_factor = None
        self._center = None

        # Only set if they are given. They're set during _set_range if None
        if scale_factor is not None:
            self.scale_factor = scale_factor
        if center is not None:
            self.center = center

    def viewbox_mouse_event(self, event):
        """ The ViewBox received a mouse event; update transform
        accordingly.
        Default implementation adjusts scale factor when scolling.
        """
        BaseCamera.viewbox_mouse_event(self, event)
        if event.type == 'mouse_wheel':
            s = 1.1 ** - event.delta[1]
            self._scale_factor *= s
            if self._distance is not None:
                self._distance *= s
            self.view_changed()

    @property
    def scale_factor(self):
        """ The measure for the scale or range that the camera should cover

        For the PanZoomCamera and TurnTableCamera this translates to
        zooming: set to smaller values to zoom in.
        """
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale_factor = abs(float(value))
        self.view_changed()

    @property
    def near_clip_distance(self):
        """ The distance of the near clipping plane from the camera's position.
        """
        return self._near_clip_distance

    def _set_range(self, init):
        """ Reset the camera view using the known limits.
        """

        if init and (self._scale_factor is not None):
            return  # We don't have to set our scale factor

        # Get window size (and store factor now to sync with resizing)
        w, h = self._viewbox.size
        w, h = float(w), float(h)

        # Get range and translation for x and y
        x1, y1, z1 = self._xlim[0], self._ylim[0], self._zlim[0]
        x2, y2, z2 = self._xlim[1], self._ylim[1], self._zlim[1]
        rx, ry, rz = (x2 - x1), (y2 - y1), (z2 - z1)

        # Correct ranges for window size. Note that the window width
        # influences the x and y data range, while the height influences
        # the z data range.
        if w / h > 1:
            rx /= w / h
            ry /= w / h
        else:
            rz /= h / w

        # Convert to screen coordinates. In screen x, only x and y have effect.
        # In screen y, all three dimensions have effect. The idea of the lines
        # below is to calculate the range on screen when that will fit the
        # data under any rotation.
        rxs = (rx**2 + ry**2)**0.5
        rys = (rx**2 + ry**2 + rz**2)**0.5

        self.scale_factor = max(rxs, rys) * 1.04  # 4% extra space

    def viewbox_resize_event(self, event):
        self.view_changed()

    def _update_transform(self, event=None):
        # Do we have a viewbox
        if self._viewbox is None:
            return

        # Calculate viewing range for x and y
        fx = fy = self._scale_factor

        # Correct for window size
        w, h = self._viewbox.size
        if w / h > 1:
            fx *= w / h
        else:
            fy *= h / w

        self._update_projection_transform(fx, fy)

        # assemble complete transform mapping to viewbox bounds
        unit = [[-1, 1], [1, -1]]
        vrect = [[0, 0], self._viewbox.size]
        self._viewbox_tr.set_mapping(unit, vrect)
        transforms = [n.transform for n in
                      self._viewbox.scene.node_path_to_child(self)[1:]]
        camera_tr = self._transform_cache.get(transforms).inverse
        full_tr = self._transform_cache.get([self._viewbox_tr,
                                             self._projection,
                                             camera_tr])
        self._transform_cache.roll()
        self._set_scene_transform(full_tr)

    def _update_projection_transform(self, fx, fy):
        d = self._get_depth_value()
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, 0, d)
        else:
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(d)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)


class Base3DRotationCamera(PerspectiveCamera):
    """Base class for TurntableCamera and ArcballCamera"""

    def __init__(self, fov=0.0, **kwargs):
        super(Base3DRotationCamera, self).__init__(fov=fov, **kwargs)
        self._actual_distance = 0.0
        self._event_value = None

    @property
    def distance(self):
        """ The user-set distance. If None (default), the distance is
        internally calculated from the scale factor and fov.
        """
        return self._distance

    @distance.setter
    def distance(self, distance):
        if distance is None:
            self._distance = None
        else:
            self._distance = float(distance)
        self.view_changed()

    def viewbox_mouse_event(self, event):
        """
        The viewbox received a mouse event; update transform
        accordingly.
        """
        if event.handled or not self.interactive:
            return

        PerspectiveCamera.viewbox_mouse_event(self, event)

        if event.type == 'mouse_release':
            self._event_value = None  # Reset

        elif event.type == 'mouse_move':
            if event.press_event is None:
                return

            modifiers = event.mouse_event.modifiers
            p1 = event.mouse_event.press_event.pos
            p2 = event.mouse_event.pos
            d = p2 - p1

            if 1 in event.buttons and not modifiers:
                # Rotate
                self._update_rotation(event)

            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = (self._scale_factor, self._distance)
                zoomy = (1 + self.zoom_factor) ** d[1]
                
                self.scale_factor = self._event_value[0] * zoomy
                # Modify distance if its given
                if self._distance is not None:
                    self._distance = self._event_value[1] * zoomy
                self.view_changed()

            elif 1 in event.buttons and keys.SHIFT in modifiers:
                # Translate
                norm = np.mean(self._viewbox.size)
                if self._event_value is None:
                    self._event_value = self.center
                dist = (p1 - p2) / norm * self._scale_factor
                dist[1] *= -1
                # Black magic part 1: turn 2D into 3D translations
                dx, dy, dz = self._dist_to_trans(dist)
                # Black magic part 2: take up-vector and flipping into account
                ff = self._flip_factors
                up, forward, right = self._get_dim_vectors()
                dx, dy, dz = right * dx + forward * dy + up * dz
                dx, dy, dz = ff[0] * dx, ff[1] * dy, dz * ff[2]
                c = self._event_value
                self.center = c[0] + dx, c[1] + dy, c[2] + dz

            elif 2 in event.buttons and keys.SHIFT in modifiers:
                # Change fov
                if self._event_value is None:
                    self._event_value = self._fov
                fov = self._event_value - d[1] / 5.0
                self.fov = min(180.0, max(0.0, fov))

    def _update_camera_pos(self):
        """ Set the camera position and orientation"""

        # transform will be updated several times; do not update camera
        # transform until we are done.
        ch_em = self.events.transform_change
        with ch_em.blocker(self._update_transform):
            tr = self.transform
            tr.reset()

            up, forward, right = self._get_dim_vectors()

            # Create mapping so correct dim is up
            pp1 = np.array([(0, 0, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0)])
            pp2 = np.array([(0, 0, 0), forward, right, up])
            tr.set_mapping(pp1, pp2)

            tr.translate(-self._actual_distance * forward)
            self._rotate_tr()
            tr.scale([1.0/a for a in self._flip_factors])
            tr.translate(np.array(self.center))

    def _get_dim_vectors(self):
        # Specify up and forward vector
        M = {'+z': [(0, 0, +1), (0, 1, 0)],
             '-z': [(0, 0, -1), (0, 1, 0)],
             '+y': [(0, +1, 0), (1, 0, 0)],
             '-y': [(0, -1, 0), (1, 0, 0)],
             '+x': [(+1, 0, 0), (0, 0, 1)],
             '-x': [(-1, 0, 0), (0, 0, 1)],
             }
        up, forward = M[self.up]
        right = np.cross(forward, up)
        return np.array(up), np.array(forward), right

    def _update_projection_transform(self, fx, fy):
        d = self._get_depth_value()
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, -d, d)
            self._actual_distance = self._distance or 0.0
        else:
            # Figure distance to center in order to have correct FoV and fy.
            # Use that auto-distance, or the given distance (if not None).
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            self._actual_distance = dist = self._distance or dist
            val = math.sqrt(d*10)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)
        # Update camera pos, which will use our calculated _distance to offset
        # the camera
        self._update_camera_pos()

    def _update_rotation(self, event):
        """Update rotation parmeters based on mouse movement"""
        raise NotImplementedError

    def _rotate_tr(self):
        """Rotate the transformation matrix based on camera parameters"""
        raise NotImplementedError

    def _dist_to_trans(self, dist):
        """Convert mouse x, y movement into x, y, z translations"""
        raise NotImplementedError


class TurntableCamera(Base3DRotationCamera):
    """ 3D camera class that orbits around a center point while
    maintaining a view on a center point.

    For this camera, the ``scale_factor`` indicates the zoom level, and
    the ``center`` indicates the position to put at the center of the
    view.

    Parameters
    ----------
    fov : float
        Field of view. Zero (default) means orthographic projection.
    elevation : float
        Elevation angle in degrees. Positive angles place the camera
        above the cente point, negative angles place the camera below
        the center point.
    azimuth : float
        Azimuth angle in degrees. Zero degrees places the camera on the
        positive x-axis, pointing in the negative x direction.
    roll : float
        Roll angle in degrees
    distance : float | None
        The distance of the camera from the rotation point (only makes sense
        if fov > 0). If None (default) the distance is determined from the
        scale_factor and fov.
    See BaseCamera for more.

    Interaction
    -----------
    * LMB: orbits the view around its center point.
    * RMB or scroll: change scale_factor (i.e. zoom level)
    * SHIFT + LMB: translate the center point
    * SHIFT + RMB: change FOV
    """

    _state_props = Base3DRotationCamera._state_props + ('elevation',
                                                        'azimuth', 'roll')

    def __init__(self, fov=0.0, elevation=30.0, azimuth=30.0, roll=0.0,
                 distance=None, **kwargs):
        super(TurntableCamera, self).__init__(fov=fov, **kwargs)

        # Set camera attributes
        self.azimuth = azimuth
        self.elevation = elevation
        self.roll = roll  # interaction not implemented yet
        self.distance = distance  # None means auto-distance

    @property
    def elevation(self):
        """ The angle of the camera in degrees above the horizontal (x, z)
        plane.
        """
        return self._elevation

    @elevation.setter
    def elevation(self, elev):
        elev = float(elev)
        self._elevation = min(90, max(-90, elev))
        self.view_changed()

    @property
    def azimuth(self):
        """ The angle of the camera in degrees around the y axis. An angle of
        0 places the camera within the (y, z) plane.
        """
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azim):
        azim = float(azim)
        while azim < -180:
            azim += 360
        while azim > 180:
            azim -= 360
        self._azimuth = azim
        self.view_changed()

    @property
    def roll(self):
        """ The angle of the camera in degrees around the z axis. An angle of
        0 places puts the camera upright.
        """
        return self._roll

    @roll.setter
    def roll(self, roll):
        roll = float(roll)
        while roll < -180:
            roll += 360
        while roll > 180:
            roll -= 360
        self._roll = roll
        self.view_changed()

    def orbit(self, azim, elev):
        """ Orbits the camera around the center position.

        Parameters
        ----------
        azim : float
            Angle in degrees to rotate horizontally around the center point.
        elev : float
            Angle in degrees to rotate vertically around the center point.
        """
        self.azimuth += azim
        self.elevation = np.clip(self.elevation + elev, -90, 90)
        self.view_changed()

    def _update_rotation(self, event):
        """Update rotation parmeters based on mouse movement"""
        p1 = event.mouse_event.press_event.pos
        p2 = event.mouse_event.pos
        if self._event_value is None:
            self._event_value = self.azimuth, self.elevation
        self.azimuth = self._event_value[0] - (p2 - p1)[0] * 0.5
        self.elevation = self._event_value[1] + (p2 - p1)[1] * 0.5

    def _rotate_tr(self):
        """Rotate the transformation matrix based on camera parameters"""
        up, forward, right = self._get_dim_vectors()
        self.transform.rotate(self.elevation, -right)
        self.transform.rotate(self.azimuth, up)

    def _dist_to_trans(self, dist):
        """Convert mouse x, y movement into x, y, z translations"""
        rae = np.array([self.roll, self.azimuth, self.elevation]) * np.pi / 180
        sro, saz, sel = np.sin(rae)
        cro, caz, cel = np.cos(rae)
        dx = (+ dist[0] * (cro * caz + sro * sel * saz)
              + dist[1] * (sro * caz - cro * sel * saz))
        dy = (+ dist[0] * (cro * saz - sro * sel * caz)
              + dist[1] * (sro * saz + cro * sel * caz))
        dz = (- dist[0] * sro * cel + dist[1] * cro * cel)
        return dx, dy, dz


class ArcballCamera(Base3DRotationCamera):
    """ 3D camera class that orbits around a center point while
    maintaining a view on a center point.

    For this camera, the ``scale_factor`` indicates the zoom level, and
    the ``center`` indicates the position to put at the center of the
    view.

    Parameters
    ----------
    fov : float
        Field of view. Zero (default) means orthographic projection.
    distance : float | None
        The distance of the camera from the rotation point (only makes sense
        if fov > 0). If None (default) the distance is determined from the
        scale_factor and fov.
    See BaseCamera for more.

    Interaction
    -----------
    * LMB: orbits the view around its center point.
    * RMB or scroll: change scale_factor (i.e. zoom level)
    * SHIFT + LMB: translate the center point
    * SHIFT + RMB: change FOV
    """

    _state_props = Base3DRotationCamera._state_props

    def __init__(self, fov=0.0, distance=None, **kwargs):
        super(ArcballCamera, self).__init__(fov=fov, **kwargs)

        # Set camera attributes
        self._quaternion = Quaternion()
        self.distance = distance  # None means auto-distance

    def _update_rotation(self, event):
        """Update rotation parmeters based on mouse movement"""
        p2 = event.mouse_event.pos
        if self._event_value is None:
            self._event_value = p2
        wh = self._viewbox.size
        self._quaternion = (Quaternion(*_arcball(p2, wh)) *
                            Quaternion(*_arcball(self._event_value, wh)) *
                            self._quaternion)
        self._event_value = p2
        self.view_changed()

    def _rotate_tr(self):
        """Rotate the transformation matrix based on camera parameters"""
        rot, x, y, z = self._quaternion.get_axis_angle()
        up, forward, right = self._get_dim_vectors()
        self.transform.rotate(180 * rot / np.pi, (x, z, y))

    def _dist_to_trans(self, dist):
        """Convert mouse x, y movement into x, y, z translations"""
        rot, x, y, z = self._quaternion.get_axis_angle()
        tr = AffineTransform()
        tr.rotate(180 * rot / np.pi, (x, y, z))
        dx, dz, dy = np.dot(tr.matrix[:3, :3], (dist[0], dist[1], 0.))
        return dx, dy, dz

    def _get_dim_vectors(self):
        # Override vectors, camera has no sense of "up"
        return np.eye(3)[::-1]


def _arcball(xy, wh):
    """Convert x,y coordinates to w,x,y,z Quaternion parameters

    Adapted from:

    linalg library

    Copyright (c) 2010-2015, Renaud Blanch <rndblnch at gmail dot com>
    Licence at your convenience:
    GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
    BSD new <http://opensource.org/licenses/BSD-3-Clause>
    """
    x, y = xy
    w, h = wh
    r = (w + h) / 2.
    x, y = -(2. * x - w) / r, (2. * y - h) / r
    h = np.sqrt(x*x + y*y)
    return (0., x/h, y/h, 0.) if h > 1. else (0., x, y, np.sqrt(1. - h*h))


class FlyCamera(PerspectiveCamera):
    """ The fly camera provides a way to explore 3D data using an
    interaction style that resembles a flight simulator.

    For this camera, the ``scale_factor`` indicates the speed of the
    camera in units per second, and the ``center`` indicates the
    position of the camera.

    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    See BaseCamera for more.

    Interaction
    -----------
    Notice: interacting with this camera might need a bit of practice.
    The reaction to key presses can be customized by modifying the
    keymap property.

    Moving:

      * arrow keys, or WASD to move forward, backward, left and right
      * F and C keys move up and down
      * Space bar to brake

    Viewing:

      * Use the mouse while holding down LMB to control the pitch and yaw.
      * Alternatively, the pitch and yaw can be changed using the keys
        IKJL
      * The camera auto-rotates to make the bottom point down, manual
        rolling can be performed using Q and E.

    """

    # Linking this camera likely not to work very well
    _state_props = PerspectiveCamera._state_props + ('rotation', )

    def __init__(self, fov=60, rotation=None, **kwargs):

        # Motion speed vector
        self._speed = np.zeros((6,), 'float64')

        # Acceleration and braking vectors, set from keyboard
        self._brake = np.zeros((6,), 'uint8')  # bool-ish
        self._acc = np.zeros((6,), 'float64')

        # Init rotations
        self._auto_roll = True  # Whether to roll to make Z up
        self._rotation1 = Quaternion()  # The base rotation
        self._rotation2 = Quaternion()  # The delta yaw and pitch rotation

        PerspectiveCamera.__init__(self, fov=fov, **kwargs)

        # Set camera attributes
        self.rotation = rotation if (rotation is not None) else Quaternion()

        # To store data at start of interaction
        self._event_value = None

        # Whether the mouse-system wants a transform update
        self._update_from_mouse = False

        # Mapping that defines keys to thrusters
        self._keymap = {
            keys.UP: (+1, 1), keys.DOWN: (-1, 1),
            keys.RIGHT: (+1, 2), keys.LEFT: (-1, 2),
            #
            'W': (+1, 1), 'S': (-1, 1),
            'D': (+1, 2), 'A': (-1, 2),
            'F': (+1, 3), 'C': (-1, 3),
            #
            'I': (+1, 4), 'K': (-1, 4),
            'L': (+1, 5), 'J': (-1, 5),
            'Q': (+1, 6), 'E': (-1, 6),
            #
            keys.SPACE: (0, 1, 2, 3),  # 0 means brake, apply to translation
            #keys.ALT: (+5, 1),  # Turbo
        }

        # Timer. Each tick we calculate new speed and new position
        self._timer = Timer(0.01, start=False, connect=self.on_timer)

    @property
    def rotation(self):
        """ Get the full rotation. This rotation is composed of the
        normal rotation plus the extra rotation due to the current
        interaction of the user.
        """
        rotation = self._rotation2 * self._rotation1
        return rotation.normalize()

    @rotation.setter
    def rotation(self, value):
        assert isinstance(value, Quaternion)
        self._rotation1 = value

    @property
    def auto_roll(self):
        """ Whether to rotate the camera automaticall to try and attempt
        to keep Z up.
        """
        return self._auto_roll

    @auto_roll.setter
    def auto_roll(self, value):
        self._auto_roll = bool(value)

    @property
    def keymap(self):
        """ A dictionary that maps keys to thruster directions

        The keys in this dictionary are vispy key descriptions (from
        vispy.keys) or characters that represent keys. These are matched
        to the "key" attribute of key-press and key-release events.

        The values are tuples, in which the first element specifies the
        magnitude of the acceleration, using negative values for
        "backward" thrust. A value of zero means to brake. The remaining
        elements specify the dimension to which the acceleration should
        be applied. These are 1, 2, 3 for forward/backward, left/right,
        up/down, and 4, 5, 6 for pitch, yaw, roll.
        """
        return self._keymap

    def _set_range(self, init):
        """ Reset the view.
        """

        #PerspectiveCamera._set_range(self, init)

        # Stop moving
        self._speed *= 0.0

        # Get window size (and store factor now to sync with resizing)
        w, h = self._viewbox.size
        w, h = float(w), float(h)

        # Get range and translation for x and y
        x1, y1, z1 = self._xlim[0], self._ylim[0], self._zlim[0]
        x2, y2, z2 = self._xlim[1], self._ylim[1], self._zlim[1]
        rx, ry, rz = (x2 - x1), (y2 - y1), (z2 - z1)

        # Correct ranges for window size. Note that the window width
        # influences the x and y data range, while the height influences
        # the z data range.
        if w / h > 1:
            rx /= w / h
            ry /= w / h
        else:
            rz /= h / w

        # Do not convert to screen coordinates. This camera does not need
        # to fit everything on screen, but we need to estimate the scale
        # of the data in the scene.

        # Set scale, depending on data range. Initial speed is such that
        # the scene can be traversed in about three seconds.
        self._scale_factor = max(rx, ry, rz) / 3.0

        # Set initial position to a corner of the scene
        margin = np.mean([rx, ry, rz]) * 0.1
        self._center = x1 - margin, y1 - margin, z1 + margin

        # Determine initial view direction based on flip axis
        yaw = 45 * self._flip_factors[0]
        pitch = -90 - 20 * self._flip_factors[2]
        if self._flip_factors[1] < 0:
            yaw += 90 * np.sign(self._flip_factors[0])

        # Set orientation
        q1 = Quaternion.create_from_axis_angle(pitch*math.pi/180, 1, 0, 0)
        q2 = Quaternion.create_from_axis_angle(0*math.pi/180, 0, 1, 0)
        q3 = Quaternion.create_from_axis_angle(yaw*math.pi/180, 0, 0, 1)
        #
        self._rotation1 = (q1 * q2 * q3).normalize()
        self._rotation2 = Quaternion()

        # Update
        self.view_changed()

    def _get_directions(self):

        # Get reference points in reference coordinates
        #p0 = Point(0,0,0)
        pf = (0, 0, -1)  # front
        pr = (1, 0, 0)  # right
        pl = (-1, 0, 0)  # left
        pu = (0, 1, 0)  # up

        # Get total rotation
        rotation = self.rotation.inverse()

        # Transform to real coordinates
        pf = rotation.rotate_point(pf)
        pr = rotation.rotate_point(pr)
        pl = rotation.rotate_point(pl)
        pu = rotation.rotate_point(pu)

        def _normalize(p):
            L = sum(x**2 for x in p) ** 0.5
            return np.array(p, 'float64') / L

        pf = _normalize(pf)
        pr = _normalize(pr)
        pl = _normalize(pl)
        pu = _normalize(pu)

        return pf, pr, pl, pu

    def on_timer(self, event):

        # Set relative speed and acceleration
        rel_speed = event.dt
        rel_acc = 0.1

        # Get what's forward
        pf, pr, pl, pu = self._get_directions()

        # Increase speed through acceleration
        # Note that self._speed is relative. We can balance rel_acc and
        # rel_speed to get a nice smooth or direct control
        self._speed += self._acc * rel_acc

        # Reduce speed. Simulate resistance. Using brakes slows down faster.
        # Note that the way that we reduce speed, allows for higher
        # speeds if keys ar bound to higher acc values (i.e. turbo)
        reduce = np.array([0.05, 0.05, 0.05, 0.1, 0.1, 0.1])
        reduce[self._brake > 0] = 0.2
        self._speed -= self._speed * reduce
        if np.abs(self._speed).max() < 0.05:
            self._speed *= 0.0

        # --- Determine new position from translation speed

        if self._speed[:3].any():

            # Create speed vectors, use scale_factor as a reference
            dv = np.array([1.0/d for d in self._flip_factors])
            #
            vf = pf * dv * rel_speed * self._scale_factor
            vr = pr * dv * rel_speed * self._scale_factor
            vu = pu * dv * rel_speed * self._scale_factor
            direction = vf, vr, vu

            # Set position
            center_loc = np.array(self._center, dtype='float32')
            center_loc += (self._speed[0] * direction[0] +
                           self._speed[1] * direction[1] +
                           self._speed[2] * direction[2])
            self._center = tuple(center_loc)

        # --- Determine new orientation from rotation speed

        roll_angle = 0

        # Calculate manual roll (from speed)
        if self._speed[3:].any():
            angleGain = np.array([1.0, 1.5, 1.0]) * 3 * math.pi / 180
            angles = self._speed[3:] * angleGain

            q1 = Quaternion.create_from_axis_angle(angles[0], -1, 0, 0)
            q2 = Quaternion.create_from_axis_angle(angles[1], 0, 1, 0)
            q3 = Quaternion.create_from_axis_angle(angles[2], 0, 0, -1)
            q = q1 * q2 * q3
            self._rotation1 = (q * self._rotation1).normalize()

        # Calculate auto-roll
        if self.auto_roll:
            up = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[self.up[1]]
            up = np.array(up) * {'+': +1, '-': -1}[self.up[0]]

            def angle(p1, p2):
                return np.arccos(p1.dot(p2))
            #au = angle(pu, (0, 0, 1))
            ar = angle(pr, up)
            al = angle(pl, up)
            af = angle(pf, up)
            # Roll angle that's off from being leveled (in unit strength)
            roll_angle = math.sin(0.5*(al - ar))
            # Correct for pitch
            roll_angle *= abs(math.sin(af))  # abs(math.sin(au))
            if abs(roll_angle) < 0.05:
                roll_angle = 0
            if roll_angle:
                # Correct to soften the force at 90 degree angle
                roll_angle = np.sign(roll_angle) * np.abs(roll_angle)**0.5
                # Get correction for this iteration and apply
                angle_correction = 1.0 * roll_angle * math.pi / 180
                q = Quaternion.create_from_axis_angle(angle_correction,
                                                      0, 0, 1)
                self._rotation1 = (q * self._rotation1).normalize()

        # Update
        if self._speed.any() or roll_angle or self._update_from_mouse:
            self._update_from_mouse = False
            self.view_changed()

    def viewbox_key_event(self, event):

        PerspectiveCamera.viewbox_key_event(self, event)

        if event.handled or not self.interactive:
            return

        # Ensure the timer runs
        if not self._timer.running:
            self._timer.start()

        if event.key in self._keymap:
            val_dims = self._keymap[event.key]
            val = val_dims[0]
            # Brake or accelarate?
            if val == 0:
                vec = self._brake
                val = 1
            else:
                vec = self._acc
            # Set
            if event.type == 'key_release':
                val = 0
            for dim in val_dims[1:]:
                factor = 1.0
                vec[dim-1] = val * factor

    def viewbox_mouse_event(self, event):

        PerspectiveCamera.viewbox_mouse_event(self, event)

        if event.handled or not self.interactive:
            return

        if event.type == 'mouse_wheel':
            if not event.mouse_event.modifiers:
                # Move forward / backward
                self._speed[0] += 0.5 * event.delta[1]
            elif keys.SHIFT in event.mouse_event.modifiers:
                # Speed
                s = 1.1 ** - event.delta[1]
                self.scale_factor /= s  # divide instead of multiply
                print('scale factor: %1.1f units/s' % self.scale_factor)
            return

        if event.type == 'mouse_release':
            # Reset
            self._event_value = None
            # Apply rotation
            self._rotation1 = (self._rotation2 * self._rotation1).normalize()
            self._rotation2 = Quaternion()
        elif not self._timer.running:
            # Ensure the timer runs
            self._timer.start()

        if event.type == 'mouse_move':

            if event.press_event is None:
                return
            if not event.buttons:
                return

            # Prepare
            modifiers = event.mouse_event.modifiers
            pos1 = event.mouse_event.press_event.pos
            pos2 = event.mouse_event.pos
            w, h = self._viewbox.size

            if 1 in event.buttons and not modifiers:
                # rotate

                # get normalized delta values
                d_az = -float(pos2[0] - pos1[0]) / w
                d_el = +float(pos2[1] - pos1[1]) / h
                # Apply gain
                d_az *= - 0.5 * math.pi  # * self._speed_rot
                d_el *= + 0.5 * math.pi  # * self._speed_rot
                # Create temporary quaternions
                q_az = Quaternion.create_from_axis_angle(d_az, 0, 1, 0)
                q_el = Quaternion.create_from_axis_angle(d_el, 1, 0, 0)

                # Apply to global quaternion
                self._rotation2 = (q_el.normalize() * q_az).normalize()

            elif 2 in event.buttons and keys.CONTROL in modifiers:
                # zoom --> fov
                if self._event_value is None:
                    self._event_value = self._fov
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1c = event.map_to_canvas(p1)[:2]
                p2c = event.map_to_canvas(p2)[:2]
                d = p2c - p1c
                fov = self._event_value * math.exp(-0.01*d[1])
                self._fov = min(90.0, max(10, fov))
                print('FOV: %1.2f' % self.fov)

        # Make transform be updated on the next timer tick.
        # By doing it at timer tick, we avoid shaky behavior
        self._update_from_mouse = True

    def _update_projection_transform(self, fx, fy):
        PerspectiveCamera._update_projection_transform(self, fx, fy)

        # Turn our internal quaternion representation into rotation
        # of our transform

        axis_angle = self.rotation.get_axis_angle()
        angle = axis_angle[0] * 180 / math.pi

        tr = self.transform
        tr.reset()
        #
        tr.rotate(-angle, axis_angle[1:])
        tr.scale([1.0/a for a in self._flip_factors])
        tr.translate(self._center)


#class FirstPersonCamera(PerspectiveCamera):
#    pass
