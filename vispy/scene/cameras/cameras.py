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

sind = lambda q: math.sin(q*math.pi/180)
cosd = lambda q: math.cos(q*math.pi/180)

# todo: maybe aspect ratio should be properties of viewbox?
# todo: allow panzoom camera to operate in other planes than Z


def make_camera(cam_type, *args, **kwds):
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
                    TurntableCamera, FlyCamera):
        cam_types[camType.__name__[:-6].lower()] = camType
    
    try: 
        return cam_types[cam_type](*args, **kwds)
    except KeyError:
        raise KeyError('Unknown camera type "%s". Options are: %s' % 
                       (cam_type, cam_types.keys()))


def get_depth_value():
    """ Get the depth value to use in orthographic and perspective projection
    
    For 24 bits and more, we're fine with 100.000, but for 16 bits we
    need 3000 or so. The criterion is that at the center, we should be
    able to distinguish between 0.1, 0.0 and -0.1 etc. 
    """
    if True:  # bit+depth >= 24
        return 100000.0
    else:
        return 3000.0


def depth_to_z(depth):
    """ Get the z-coord, given the depth value. 
    """
    val = get_depth_value()
    return val - depth * 2 * val


def _zoomfactor(d):
    """ Define here to force same zoom feeling on cameras.
    """
    return 1.0 / math.exp(-0.005*d)


class BaseCamera(Node):
    """ Base camera class.
    
    The Camera describes the perspective from which a ViewBox views its 
    subscene, and the way that user interaction affects that perspective.
    
    Most functionality is implemented in subclasses. This base class has
    no user interaction and causes the subscene to use the same coordinate
    system as the ViewBox.
    
    Parameters
    ----------
    scale_factor : scalar
        A measure for the scale/range of the scene that the camera
        should show. The exact meaning differs per camera type.
    center : tuple of scalars
        The center position. The exact meaning differs per camera type.
    aspect_ratio : tuple of scalars
        The aspect ratio (i.e. scaling) of each dimension.
    aspect_fixed : bool
        Whether the aspect ratio is fixed. Default False. If False, the
        camera will adjust the aspect ratio depending on e.g. screen
        dimensions.
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    
    """
    
    # These define the state of the camera
    _state_props = ('scale_factor', 'aspect_ratio', 'aspect_fixed', 
                    'center', 'fov')
    
    def __init__(self, interactive=True, scale_factor=None, center=None, 
                 aspect_ratio=None, aspect_fixed=False,
                 **kwargs):
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
        
        # To adjust daspect when resizing
        self._window_size_factor = 0
        
        # For internal use, to store event related information
        self._event_value = None
        
        # Reset management
        self._resetting = False  # Avoid lots of updates during a reset
        
        # Limits set in reset (interesting region of the scene)
        self._xlim = None  # None is flag that no reset has been performed
        self._ylim = None
        self._zlim = None
        
        # View parameters
        self._fov = 0.0
        self._scale_factor = 1.0
        self._aspect_ratio = 1.0, 1.0, 1.0
        self._aspect_ratio_n = 1.0, 1.0, 1.0  # normalized version
        self._center_loc = 0.0, 0.0, 0.0
        
        # Indirect view parameters (not set during reset)
        self._interactive = bool(interactive)
        self._aspect_fixed = bool(aspect_fixed)
        
        # Keep track of parameters given at initialization, so that we
        # can set then after reset
        self._given_params = {}
        
        # Init things that may be set depening on bounds
        if scale_factor is not None:
            self._given_params['scale_factor'] = scale_factor
        if center is not None:
            self._given_params['center'] = center
        if aspect_ratio is not None:
            self._given_params['aspect_ratio'] = aspect_ratio
    
    def _viewbox_set(self, viewbox):
        """ Friend method of viewbox to register itself.
        """
        self._viewbox = viewbox
        # Connect
        viewbox.events.mouse_press.connect(self.view_mouse_event)
        viewbox.events.mouse_release.connect(self.view_mouse_event)
        viewbox.events.mouse_move.connect(self.view_mouse_event)
        viewbox.events.mouse_wheel.connect(self.view_mouse_event)
        viewbox.events.resize.connect(self.view_resize_event)
        # todo: also add key events! (and also on viewbox (they're missing)
    
    def _viewbox_unset(self, viewbox):
        """ Friend method of viewbox to unregister itself.
        """
        self._viewbox = None
        # Disconnect
        viewbox.events.mouse_press.disconnect(self.view_mouse_event)
        viewbox.events.mouse_release.disconnect(self.view_mouse_event)
        viewbox.events.mouse_move.disconnect(self.view_mouse_event)
        viewbox.events.mouse_wheel.disconnect(self.view_mouse_event)
        viewbox.events.resize.disconnect(self.view_resize_event)
    
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
    def aspect_ratio(self):
        """ The aspect ratio to show the scene with
        
        E.g. (0.5, 1.0, 1.0) would make the x-dimension half as small.
        Negative values can be used to flip dimensions, e.g. (1, -1)
        is typically suited for visualizing images.
        """
        return self._aspect_ratio
    
    @aspect_ratio.setter
    def aspect_ratio(self, value):
        # Check and prepare
        if len(value) == 2:
            value = float(value[0]), float(value[1]), 1.0
        elif len(value) == 3:
            value = float(value[0]), float(value[1]), float(value[2])
        else:
            raise ValueError('Aspect ratio must be a 2 or 3 element tuple')
        # Normalize
        self._aspect_ratio = value
        self._aspect_ratio_n = tuple([v / abs(value[0]) for v in value])
        self.view_changed()
    
    @property
    def aspect_fixed(self):
        """ Whether the aspect ratio is fixed
        
        If not fixed, the camera is allowed to modify the aspect ratio
        during resetting, window resizing, and interaction.
        """
        return self._aspect_fixed
    
    @aspect_fixed.setter
    def aspect_fixed(self, value):
        self._aspect_fixed = bool(value)
    
    @property
    def center(self):
        """ The center location for this camera
        
        The exact meaning of this value differs per type of camera, but
        generally means the point of interest or the rotation point.
        """
        return self._center_loc or (0, 0, 0)
    
    @center.setter
    def center(self, val):
        if len(val) == 2:
            self._center_loc = float(val[0]), float(val[1]), 0.0
        elif len(val) == 3:
            self._center_loc = float(val[0]), float(val[1]), float(val[2])
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
    
    def set_range(self, xrange=None, yrange=None, zrange=None, margin=0.05):
        """ Set the range of the view region for the camera
        
        The view is reset to the given range or to the scene boundaries
        if ranges are not specified. The ranges should be 2-element
        tuples specifying the min and max for each dimension.
        """
        # Do we have a viewbox?
        if self._viewbox is None:
            return
        self._resetting = True
        # Size factor
        size = self._viewbox.size
        self._window_size_factor = size[1] / size[0]
        # Get bounds
        bounds = []
        bounds_scene = self._viewbox.get_scene_bounds()
        for i, lim in enumerate((xrange, yrange, zrange)):
            if lim is None:
                bounds.append(bounds_scene[i])
            else:
                bounds.append((float(lim[0]), float(lim[1])))
        # Calculate ranges and margins
        ranges = [b[1] - b[0] for b in bounds]
        margins = [(r*margin or 0.1) for r in ranges]
        # Assign limits for this camera
        bounds_margins = [(b[0]-m, b[1]+m) for b, m in zip(bounds, margins)]
        self._xlim, self._ylim, self._zlim = bounds_margins
        # Store center location
        self._center_loc = [(b[0] + r / 2) for b, r in zip(bounds, ranges)]
        # Set given params (since _set_range() might derive other values)
        for name, value in self._given_params.items():
            setattr(self, name, value)
        # Let specific camera handle it
        self._set_range()
        # Overwrite given params
        for name, value in self._given_params.items():
            setattr(self, name, value)
        # Finish reset
        self._resetting = False
        self.view_changed()
    
    def _set_range(self):
        pass 
    
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
    
    def view_changed(self):
        """ Called when this camera is connected to a new view.
        """
        if self._resetting:
            return
        # Reset if necessary (and if we can)
        if (self._xlim is None) and (self._viewbox is not None):
            self.set_range()
        # Update if there is a viewbox
        if self._viewbox:
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
    
    def view_mouse_event(self, event):
        """ The ViewBox received a mouse event; update transform 
        accordingly.
        Default implementation adjusts scale factor when scolling.
        """
        if event.type == 'mouse_wheel':
            s = 1.1 ** - event.delta[1]
            self._scale_factor *= s
            self.view_changed()
    
    def view_resize_event(self, event):
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
    See BaseCamera.
    
    Interaction
    -----------
    * LMB: pan the view
    * RMB or scroll: zooms the view
    
    """
    def __init__(self, **kwargs):
        super(PanZoomCamera, self).__init__(**kwargs)
        # todo: Y axis is flipped by default?
        #self._aspect_ratio = self._aspect_ratio_n = 1.0, -1.0, 0.0
        self.transform = STTransform()
    
    def zoom(self, scale_factor, center):
        """ Focus the view at the given center with the given scale factor
        
        Parameters
        ----------
        scale_factor : float
            The scale factor. Set to smaller values to zoom in.
        center : tuple of 2 or 3 elements
            The center of the view
        """
        self.scale_factor = scale_factor
        self.center = center
    
    def pan(self, pan):
        """ Pan the view.
        
        Parameters
        ----------
        pan : length-2 sequence
            The distance to pan the view, in the coordinate system of the 
            scene.
        """
        self.rect = self.rect + pan
    
    @property
    def rect(self):
        """ The rectangular border of the ViewBox visible area, expressed in
        the coordinate system of the scene.
        
        By definition, the +y axis of this rect is opposite the +y axis of the
        ViewBox. 
        """
        sf = self._scale_factor
        naspect = self._aspect_ratio_n
        c = self.center
        r = Rect(c[0] - naspect[0] * 0.5 * sf, c[1] - naspect[1] * 0.5 * sf,
                 naspect[0] * sf, naspect[1] * sf)
        return r
        
    @rect.setter
    def rect(self, args):
        """
        Set the bounding rect of the visible area in the subscene. 
        
        By definition, the +y axis of this rect is opposite the +y axis of the
        ViewBox. 
        """
        if isinstance(args, tuple):
            rect = Rect(*args)
        else:
            rect = Rect(args)
        self._rect = rect
        self.set_range((rect.left, rect.right), (rect.bottom, rect.top), 
                       (-1, 1), margin=0)
    
    def _set_range(self):
        
        rx = self._xlim[1] - self._xlim[0]
        ry = self._ylim[1] - self._ylim[0]
        
        # Get window size (and store factor now to sync with resizing)
        w, h = self._viewbox.size
        w, h = float(w), float(h)
        
        # Correct ranges for window size.
        if w / h > 1:
            rx /= w/h
        else:
            ry /= h/w
    
        # Set scale factor (and maybe aspect ratio)
        if not self._aspect_fixed:
            ars = np.sign(self._aspect_ratio)
            self.aspect_ratio = ars[0], ars[1] * rx / ry, ars[2]
            self._scale_factor = rx
        else:
            self._scale_factor = max(rx, ry * abs(self._aspect_ratio_n[1]))
        
        self.view_changed()
    
    def view_resize_event(self, event):
        """ Modify the data aspect and scale factor, to adjust to
        the new window size.
        """
        # Get new size factor
        w, h = self._viewbox.size
        
        size_factor1 = h / w
        # Get old size factor
        size_factor2 = self._window_size_factor
        # Update
        self._window_size_factor = size_factor1
        
        # Make it quick if daspect is not in auto-mode
        if self._aspect_fixed:
            self.view_changed()
            return
        
        # Get daspect factor
        daspect_factor = size_factor1
        if size_factor2:
            daspect_factor /= size_factor2
        
        # Get zoom factor
        zoomFactor = 1.0
        if size_factor1 < 1:
            zoomFactor /= size_factor1
        if size_factor2 and size_factor2 < 1:
            zoomFactor *= size_factor2
        
        # Change daspect and zoom
        ar = self._aspect_ratio_n
        self.aspect_ratio = ar[0], ar[1] * daspect_factor
        self._scale_factor /= zoomFactor
        
        self.view_changed()
    
    def view_mouse_event(self, event):
        """
        The SubScene received a mouse event; update transform 
        accordingly.
        """
        if event.handled or not self.interactive:
            return
        
        # Scrolling
        BaseCamera.view_mouse_event(self, event)
        
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
                # Translate
                if self._event_value is None:
                    self._event_value = self.center
                p1s = self._scene_transform.imap(p1)
                p2s = self._scene_transform.imap(p2)
                self.center = (self._event_value[0] + (p1s[0] - p2s[0]),
                               self._event_value[1] + (p1s[1] - p2s[1]),
                               self._event_value[2])
            
            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = self._scale_factor, self._aspect_ratio
                zoomx, zoomy = _zoomfactor(-d[0]), _zoomfactor(d[1])
                if not self._aspect_fixed: 
                    self.scale_factor = self._event_value[0] * zoomx
                    prev_ar = self._event_value[1]
                    self.aspect_ratio = 1, prev_ar[1]*zoomx/zoomy
                else:
                    self.scale_factor = self._event_value[0] * zoomy
    
    def _update_transform(self):
        
        # Viewbox transform
        unit = [[-1, 1], [1, -1]]
        vrect = [[0, 0], self._viewbox.size]
        self._viewbox_tr.set_mapping(unit, vrect)
        
        # Our transform
        #self.transform.reset()
        self.transform.scale = 1, 1, 1
        self.transform.translate = 0, 0, 0
        self.transform.zoom([1.0/a for a in self._aspect_ratio_n])
        self.transform.move(self.center)
        
        # Projection
        fx = fy = self.scale_factor
        w, h = self._viewbox.size
        if w / h > 1:
            fx *= w/h
        else:
            fy *= h/w
        #
        d = get_depth_value()
        self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, 0, d)
        
        # Create full transform
        transforms = [n.transform for n in
                      self._viewbox.scene.node_path_to_child(self)[1:]]
        camera_tr = self._transform_cache.get(transforms).inverse
        full_tr = self._transform_cache.get([self._viewbox_tr,
                                             self._projection,
                                             camera_tr])
        self._set_scene_transform(full_tr)


class PerspectiveCamera(BaseCamera):
    """ Base class for 3D cameras supporting orthographic and
    perspective projections.
    
    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    See BaseCamera for more.
    
    """
    def __init__(self, fov=60.0, **kwargs):
        super(PerspectiveCamera, self).__init__(**kwargs)
        # Camera transform
        self.transform = AffineTransform()
        
        # Init fov - does not depend on bounds
        self._fov = None
        self._given_params['fov'] = fov
    
    @property
    def near_clip_distance(self):
        """ The distance of the near clipping plane from the camera's position.
        """
        return self._near_clip_distance
    
    def _set_range(self):
        pass
    
    def view_resize_event(self, event):
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
        d = get_depth_value()
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, 0, d)
        else:
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(d)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)


class TurntableCamera(PerspectiveCamera):
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
        Elevation in degrees.
    azimuth : float
        Azimuth in degrees.
    See BaseCamera for more.
    
    Interaction
    -----------
    * LMB: orbits the view around its center point.
    * RMB or scroll: change scale_factor (i.e. zoom level)
    * SHIFT + LMB: translate the center point
    * SHIFT + RMB: change FOV
    
    """
    
    _state_props = BaseCamera._state_props + ('elevation', 'azimuth')
    
    def __init__(self, fov=0.0, elevation=0.0, azimuth=0.0, up='z', **kwds):
        super(TurntableCamera, self).__init__(fov=fov, **kwds)
        # Init variables
        self._elevation = 0.0
        self._azimuth = 0.0
        self._roll = 0.0  # not implemented yet
        self._distance = 0.0
        self.up = up
        self._event_value = None
        # Init for real
        
        # Init view parameters to set upon reset
        self._given_params['elevation'] = elevation
        self._given_params['azimuth'] = azimuth
    
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
    
    def _set_range(self):
        """ Reset the camera view using the known limits.
        """
        
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
        
        # If auto-scale is on, change aspect ratio, x is the reference
        if not self._aspect_fixed:
            self.aspect_ratio = 1.0, rx/ry, rx/rz
        
        # Correct for aspect ratio
        nar = self._aspect_ratio_n
        rx, ry, rz = abs(rx * nar[0]), abs(ry * nar[1]), abs(rz * nar[2])
        
        # Convert to screen coordinates. In screen x, only x and y have effect.
        # In screen y, all three dimensions have effect. The idea of the lines
        # below is to calculate the range on screen when that will fit the 
        # data under any rotation.
        rxs = (rx**2 + ry**2)**0.5
        rys = (rx**2 + ry**2 + rz**2)**0.5
        
        self._scale_factor = max(rxs, rys) * 1.04  # 4% extra space
        self.view_changed()
    
    def view_resize_event(self, event):
        """ Modify the data aspect and scale factor, to adjust to
        the new window size.
        """
        # Get new size factor
        w, h = self._viewbox.size
        size_factor1 = h / w
        # Get old size factor
        size_factor2 = self._window_size_factor
        # Update
        self._window_size_factor = size_factor1
        
        # Make it quick if daspect is not in auto-mode
        if self._aspect_fixed:
            self.view_changed()
            return
        
        # Get daspect factor
        daspect_factor = size_factor1
        if size_factor2:
            daspect_factor /= size_factor2
        
        # Get zoom factor
        zoomFactor = 1.0
        if size_factor1 < 1:
            zoomFactor /= size_factor1
        if size_factor2 and size_factor2 < 1:
            zoomFactor *= size_factor2
        
        # Change daspect and zoom
        ar = self._aspect_ratio_n
        self.aspect_ratio = ar[0], ar[1], ar[2] * daspect_factor
        self._scale_factor /= zoomFactor
        
        self.view_changed()
    
    def view_mouse_event(self, event):
        """
        The viewbox received a mouse event; update transform 
        accordingly.
        """
        if event.handled or not self.interactive:
            return
        
        # Scrolling
        BaseCamera.view_mouse_event(self, event)
        
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
                if self._event_value is None:
                    self._event_value = self.azimuth, self.elevation
                self.azimuth = self._event_value[0] - (p2 - p1)[0] * 0.5
                self.elevation = self._event_value[1] + (p2 - p1)[1] * 0.5
            
            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = self._scale_factor, self._aspect_ratio
                zoomx, zoomy = _zoomfactor(-d[0]), _zoomfactor(d[1])
                if not self._aspect_fixed:
                    self.scale_factor = self._event_value[0] * zoomx
                    prev_ar = self._event_value[1]
                    self.aspect_ratio = (prev_ar[0] * zoomy/zoomx, 
                                         prev_ar[1] * zoomy/zoomx, 
                                         prev_ar[2])
                else:
                    self.scale_factor = self._event_value[0] * zoomy
                self.view_changed()
            
            elif 1 in event.buttons and keys.SHIFT in modifiers:
                # Translate
                w = self._viewbox.size[0]
                if self._event_value is None:
                    self._event_value = self.center
                dist = (p1 - p2) / w * self._scale_factor
                dist[1] *= -1
                ar = self._aspect_ratio_n
                #
                sro, saz, sel = list(map(sind, (self._roll, self._azimuth, 
                                                self._elevation)))
                cro, caz, cel = list(map(cosd, (self._roll, self._azimuth, 
                                                self._elevation)))
                dx = (+ dist[0] * (cro * caz + sro * sel * saz)
                      + dist[1] * (sro * caz - cro * sel * saz)) / ar[0]
                dy = (+ dist[0] * (cro * saz - sro * sel * caz) 
                      + dist[1] * (sro * saz + cro * sel * caz)) / ar[1]
                dz = (- dist[0] * sro * cel + dist[1] * cro * cel) / ar[2]
                #
                c = self._event_value
                self.center = c[0] + dx, c[1] + dy, c[2] + dz
            
            elif 2 in event.buttons and keys.SHIFT in modifiers:
                # Change fov
                if self._event_value is None:
                    self._event_value = self._fov
                fov = self._event_value - d[1] / 5.0
                self.fov = min(180.0, max(0.0, fov))
                print('FOV: %1.2f' % self.fov)
    
    def _update_camera_pos(self):
        """ Set the camera position / orientation based on elevation,
        azimuth, distance, and center properties.
        """
        
        # transform will be updated several times; do not update camera
        # transform until we are done.
        ch_em = self.events.transform_change
        with ch_em.blocker(self._update_transform):
            tr = self.transform
            tr.reset()
            if self.up == 'y':
                tr.translate((0.0, 0.0, -self._distance))
                tr.rotate(self.elevation, (-1, 0, 0))
                tr.rotate(self.azimuth, (0, 1, 0))
            elif self.up == 'z':
                tr.rotate(90, (1, 0, 0))
                tr.translate((0.0, -self._distance, 0.0))
                tr.rotate(self.elevation, (-1, 0, 0))
                tr.rotate(self.azimuth, (0, 0, 1))
            else:
                raise ValueError('TurntableCamera.up must be "y" or "z".')
            
            tr.scale([1.0/a for a in self._aspect_ratio_n])
            tr.translate(np.array(self.center))
    
    def _update_projection_transform(self, fx, fy):
        d = get_depth_value()
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, -d, d)
            self._distance = 0.0
        else:
            # Figure distance to center in order to have correct FoV and fy.
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(d*10)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)
            self._distance = dist
        # Update camera pos, which will use our calculated _distance to offset
        # the camera
        self._update_camera_pos()


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
    _state_props = ('_rotation1', '_rotation2') + BaseCamera._state_props

    def __init__(self, fov=60, **kwargs):
        
        # Motion speed vector
        self._speed = np.zeros((6,), 'float64')
        
        # Acceleration and braking vectors, set from keyboard
        self._brake = np.zeros((6,), 'uint8')  # bool-ish
        self._acc = np.zeros((6,), 'float64')
        
        # Init rotations
        self._auto_roll = True  # Whether to roll to make Z up
        self._rotation1 = Quaternion()  # The total totation
        self._rotation2 = Quaternion()  # The delta yaw and pitch rotation
        
        PerspectiveCamera.__init__(self, fov=fov, **kwargs)
        
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
        self._key_events_bound = False
        
        # Timer. Each tick we calculate new speed and new position
        self._timer = Timer(0.01, start=False, connect=self.on_timer)
     
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
    
    @property
    def _rotation(self):
        """ Get the full rotation for internal use. This rotation is composed
        of the normal rotation plus the extra rotation due to the current 
        interaction of the user.
        """
        rotation = self._rotation2 * self._rotation1
        return rotation.normalize()
    
    def _set_range(self):
        """ Reset the view.
        """
        
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
        
        # If auto-scale is on, change aspect ratio, x is the reference
        if not self._aspect_fixed:
            self.aspect_ratio = 1.0, rx/ry, rx/rz
        
        # Correct for aspect ratio
        nar = self._aspect_ratio_n
        rx, ry, rz = abs(rx * nar[0]), abs(ry * nar[1]), abs(rz * nar[2])
        
        # Do not convert to screen coordinates. This camera does not need
        # to fit everything on screen, but we need to estimate the scale
        # of the data in the scene.
        
        # Set scale, depending on data range. Initial speed is such that
        # the scene can be traversed in about three seconds.
        self._scale_factor = max(rx, ry, rz) / 3.0 
        
        # Set initial position to a corner of the scene
        margin = np.mean([rx, ry, rz]) * 0.1
        self._center_loc = x1 - margin, y1 - margin, z1 + margin
        
        # Determine initial view direction based on flip axis
        yaw = 45 * np.sign(self._aspect_ratio_n[0])
        pitch = -90 - 20 * np.sign(self._aspect_ratio_n[2])
        if self._aspect_ratio_n[1] < 0:
            yaw += 90 * np.sign(self._aspect_ratio_n[0])
        
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
        rotation = self._rotation.inverse()
        
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
            dv = np.array([1.0/d for d in self._aspect_ratio_n])
            #
            vf = pf * dv * rel_speed * self._scale_factor
            vr = pr * dv * rel_speed * self._scale_factor
            vu = pu * dv * rel_speed * self._scale_factor
            direction = vf, vr, vu
            
            # Set position
            center_loc = np.array(self._center_loc, dtype='float32')
            center_loc += (self._speed[0] * direction[0] + 
                           self._speed[1] * direction[1] +
                           self._speed[2] * direction[2])
            self._center_loc = tuple(center_loc)
        
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
            angle = lambda p1, p2: np.arccos(p1.dot(p2))
            #au = angle(pu, (0, 0, 1))
            ar = angle(pr, (0, 0, 1))
            al = angle(pl, (0, 0, 1))
            af = angle(pf, (0, 0, 1))
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
    
    def view_key_event(self, event):
        
        if event.handled or not self.interactive:
            return
        
        # todo: connect this method to viewbox.events.key_down
        # viewbox does not currently support key events
        
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
    
    def view_mouse_event(self, event):
        
        # A bit awkward way to connect to our canvas; we need event
        # object to get a reference to the canvas
        if not self._key_events_bound:
            self._key_events_bound = True
            event.canvas.events.key_press.connect(self.view_key_event)
            event.canvas.events.key_release.connect(self.view_key_event)
        
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
        
        axis_angle = self._rotation.get_axis_angle()
        angle = axis_angle[0] * 180 / math.pi
        
        tr = self.transform
        tr.reset()
        #
        tr.rotate(-angle, axis_angle[1:])
        tr.scale([1.0/a for a in self._aspect_ratio_n])
        tr.translate(self._center_loc)


#class ArcballCamera(PerspectiveCamera):
#    pass


#class FirstPersonCamera(PerspectiveCamera):
#    pass
