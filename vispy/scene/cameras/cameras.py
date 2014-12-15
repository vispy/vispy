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

# todo: enable setting data aspect ratio on viewbox/scene and deal with it here


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
    return math.exp(-0.005*d)


class BaseCamera(Node):
    """ The Camera describes the perspective from which a ViewBox views its 
    subscene, and the way that user interaction affects that perspective.
    
    Most functionality is implemented in subclasses. This base class has
    no user interaction and causes the subscene to use the same coordinate
    system as the ViewBox.
    
    Parameters
    ----------
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, **kwargs):
        super(BaseCamera, self).__init__(**kwargs)
        
        # The viewboxes for which this camera is active
        self._viewboxes = []
        
        # Variables related to transforms 
        self._pre_transform = None
        self.transform = NullTransform()
        self._transform_cache = TransformCache()
        
        # Limits set in reset (interesting region of the scene)
        self._xlim = None  # None means not initialized
        self._ylim = None
        self._zlim = None
        
        # More view parameters
        self._interactive = True
        self._scale_factor = 1.0
        self._center_loc = None
        
        # For internal use, to store event related information
        self._event_value = None
    
    def _add_viewbox(self, viewbox):
        """ Friend method of viewbox to register itself.
        """
        self._viewboxes.append(viewbox)
        # Connect
        viewbox.events.mouse_press.connect(self.view_mouse_event)
        viewbox.events.mouse_release.connect(self.view_mouse_event)
        viewbox.events.mouse_move.connect(self.view_mouse_event)
        viewbox.events.mouse_wheel.connect(self.view_mouse_event)
        viewbox.events.resize.connect(self.view_resize_event)
        # todo: also add key events! (and also on viewbox (they're missing)
    
    def _remove_viewbox(self, viewbox):
        """ Friend method of viewbox to unregister itself.
        """
        self._viewboxes.remove(viewbox)
        # Disconnect
        viewbox.events.mouse_press.disconnect(self.view_mouse_event)
        viewbox.events.mouse_release.disconnect(self.view_mouse_event)
        viewbox.events.mouse_move.disconnect(self.view_mouse_event)
        viewbox.events.mouse_wheel.disconnect(self.view_mouse_event)
        viewbox.events.resize.disconnect(self.view_resize_event)
    
    def _ref_viewbox(self):
        """ The reference viewbox. This is either the first active
        viewbox, or the viewbox of the scene that we're in. Can be None
        if camera is not in a scene. Intended to be allow reset() to
        operate even if the camera is not active.
        """
        if self._viewboxes:
            # Prefer active viewbox
            return self._viewboxes[0]
        else:
            # Search viewbox upstream
            parent = self
            while parent.parents:
                parent = parent.parents[0]
                if hasattr(parent, 'scene'):
                    return parent
            else:
                return None
    
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
        """ The camera scale factor (float), representing the relative size
        of the scene. Often this translates to a zoom factor.
        """ 
        return self._scale_factor
    
    @scale_factor.setter
    def scale_factor(self, zoom):
        self._scale_factor = float(zoom)
        self.view_changed()
    
    @property
    def center(self):
        """ The center location for this camera. The exact meaning of
        this value differs per type of camera, but generally means the
        point of interest or the rotation point.
        """
        return self._center_loc or (0, 0, 0)
    
    @center.setter
    def center(self, val):
        if len(val) == 2:
            self._center_loc = float(val[0]), float(val[1]), float(val[2])
        elif len(val) == 3:
            self._center_loc = float(val[0]), float(val[1]), 0.0)
        else:
            raise ValueError('Center must be a 2 or 3 element tuple')
        self.view_changed()
    
    def reset(self, xlim=None, ylim=None, zlim=None, margin=0.05):
        """ Reset the view of this camera
        
        The view is reset to the given limits or to the scene boundaries
        if limits are not specified. The limits should be 2-element
        tuples specifying the min and max for each dimension.
        """
        # Get reference viewbox
        viewbox = self._ref_viewbox()
        if viewbox is None:
            return
        # Get bounds
        bounds = []
        bounds_scene = viewbox.get_scene_bounds()
        for i, lim in enumerate((xlim, ylim, zlim)):
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
        # Let specific camera handle it
        self._reset()
        #self._update_transform()  -> should be done in overladed method
    
    def _reset(self):
        pass 
    
    def view_changed(self):
        """ Called when this camera is connected to a new view.
        """
        # Reset if necessary (and if we can)
        if self._xlim is None:
            if self._ref_viewbox() is None:
                return
            self.reset()
        # Update if there is a viewbox
        if self._viewboxes:
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
            self._scale_factor /= s
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
            
        for viewbox in self._viewboxes:
            viewbox.scene.transform = self._scene_transform
            viewbox.update()

    
class PanZoomCamera(BaseCamera):
    """
    Camera implementing 2D pan/zoom mouse interaction. Primarily intended for
    displaying plot data.

    By default, this camera inverts the y axis of the scene. This usually 
    results in the scene +y axis pointing upward because widgets (including 
    ViewBox) have their +y axis pointing downward.
    
    User interaction:
    
    * Dragging left mouse button pans the view
    * Dragging right mouse button vertically zooms the view y-axis
    * Dragging right mouse button horizontally zooms the view x-axis
    * Mouse wheel zooms both view axes equally.

    Parameters
    ----------
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, **kwargs):
        super(PanZoomCamera, self).__init__(**kwargs)
        self._invert = [False, True]
        self._aspect_ratio = 1.0, 1.0
        self.transform = STTransform()
    
    def zoom(self, scale_factor, center):
        """ Focus the view at the given center with the given scale factor
        
        Parameters
        ----------
        scale_factor : float
            The scale factor. Larger values XXXX
        center : tuple of 2 or 3 elements
            The center of the view
        """
        # todo: docs
        
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
        sf = 1.0 / self._scale_factor
        naspect = self._aspect_ratio
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
        self.reset((rect.left, rect.right), (rect.bottom, rect.top), (-1, 1),
                   margin=0)
    
    def _reset(self):
        
        rx = self._xlim[1] - self._xlim[0]
        ry = self._ylim[1] - self._ylim[0]
        
        # Get window size (and store factor now to sync with resizing)
        viewbox = self._ref_viewbox()
        w, h = viewbox.size
        w, h = float(w), float(h)
        self._windowSizeFactor = h / w
        
        # todo: when dealing with daspect, also check examples:
        # -> nested_viewbox.py, magnify.py
        
#         # Correct ranges for window size.
#         if w / h > 1:
#             rx /= w / h
#         else:
#             ry /= h / w
        
        # Data aspect
        # By definition: x is set to 1 and we scale y accordingly
        if True:  # auto-aspect
            self._aspect_ratio = 1.0, ry / rx
        
        # Set scale
        self._scale_factor = 1 / rx
        self.view_changed()
    
    @property 
    def invert_y(self):
        # todo: remove this invavor of data aspect with negative elements
        """ Boolean indicating whether the y axis of the SubScene is inverted 
        relative to the ViewBox.
        
        Default is True--this camera inverts the y axis of the scene. In most
        cases, this results in the scene +y axis pointing upward because 
        widgets (including ViewBox) have their +y axis pointing downward.
        """
        return self._invert[1]
    
    @invert_y.setter
    def invert_y(self, inv):
        if not isinstance(inv, bool):
            raise TypeError("Invert must be boolean.")
        self._invert[1] = inv
        self.view_changed()
    
    def view_resize_event(self, event):
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
            modifiers = event.mouse_event.modifiers
            
            if event.press_event is None:
                return
            
            elif 1 in event.buttons and not modifiers:
                # Translate
                if self._event_value is None:
                    self._event_value = self.center
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1s = self._scene_transform.imap(p1)
                p2s = self._scene_transform.imap(p2)
                self.center = (self._event_value[0] + (p1s[0] - p2s[0]),
                               self._event_value[1] + (p1s[1] - p2s[1]),
                               self._event_value[2])
            
            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = self._scale_factor, self._aspect_ratio
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                d = p2 - p1
                zoomx, zoomy = _zoomfactor(-d[0]), _zoomfactor(d[1])
                if True:  # auto aspect ratio
                    self.scale_factor = self._event_value[0] * zoomx
                    prev_ar = self._event_value[1]
                    self._aspect_ratio = (1, prev_ar[1]*zoomx/zoomy)
                else:
                    self.scale_factor = self._event_value[0] * zoomy
    
    def _update_transform(self):
        viewbox = self._viewboxes[0]
        vbr = viewbox.rect.flipped(x=self._invert[0], y=self._invert[1])
        self.transform.set_mapping(self.rect, vbr)
        self._set_scene_transform(self.transform)

        
class PerspectiveCamera(BaseCamera):
    """ Base class for 3D cameras supporting orthographic and perspective
    projections.
    
    User interaction:
    
    * Dragging left mouse button orbits the view around its center point.
    * Mouse wheel changes the field of view angle.
    
    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, fov=60.0, **kwargs):
        super(PerspectiveCamera, self).__init__(**kwargs)
        # Transform for our "view"
        self._viewbox_tr = STTransform()
        self._projection = PerspectiveTransform()
        self._transform_cache = TransformCache()
        
        # Camera transform
        self.transform = AffineTransform()
        self.fov = fov
    
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
    
    @property
    def near_clip_distance(self):
        """ The distance of the near clipping plane from the camera's position.
        """
        return self._near_clip_distance
    
    def view_resize_event(self, event):
        self.view_changed()
    
    def _update_transform(self, event=None):
        # Get reference viewbox
        if not self._viewboxes:
            return
        viewbox = self._viewboxes[0]
        
        # Calculate viewing range for x and y
        fx = abs(1.0 / self._scale_factor)
        fy = abs(1.0 / self._scale_factor)
        
        # Correct for window size 
        w, h = viewbox.size
        w, h = float(w), float(h)        
        if w / h > 1:
            fx *= w / h
        else:
            fy *= h / w
        
        self._update_projection_transform(fx, fy)
        
        # assemble complete transform mapping to viewbox bounds
        unit = [[-1, 1], [1, -1]]
        vrect = [[0, 0], viewbox.size]

        self._viewbox_tr.set_mapping(unit, vrect)
        transforms = [n.transform for n in 
                      viewbox.scene.node_path_to_child(self)[1:][::-1]]
        #transforms = self.node_path_transforms(viewbox.scene)
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
    """ 3D camera class that orbits around a center point while maintaining a
    fixed vertical orientation.

    Parameters
    ----------
    fov : float
        Field of view. Zero (default) means orthographic projection.
    elevation : float
        Elevation in degrees.
    azimuth : float
        Azimuth in degrees.
    up : {'z', 'y'}
        Specify what dimension is up. Default 'z'.
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, fov=0.0, elevation=0.0, azimuth=0.0, up='z', **kwds):
        super(TurntableCamera, self).__init__(fov=fov, **kwds)
        # Init variables
        self._elevation = 0.0
        self._azimuth = 0.0
        self._distance = 0.0
        self.up = up
        self._event_value = None
        # Init for real
       
        self.elevation = elevation
        self.azimuth = azimuth
    
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
    
    def _reset(self):
        """ Reset the camera view using the known limits.
        """
        # todo: self._daspect = self.viewbox._daspect
        
        # Get reference viewbox
        viewbox = self._ref_viewbox()
        
        # Set angles
        self._elevation = 10.0
        self._azimuth = 20.0
        self._fov = 0.0
        
        # Get window size (and store factor now to sync with resizing)
        w, h = viewbox.size
        w, h = float(w), float(h)
        self._windowSizeFactor = h / w
        
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
        
        # If auto-scale is on, change daspect, x is the reference
        #if self.axes.daspectAuto:
        #    self._SetDaspect(rx/ry, 1, 0)
        #    self._SetDaspect(rx/rz, 2, 0)
        
        # Correct for normalized daspect
        #ndaspect = self.daspectNormalized
        #rx, ry, rz = abs(rx*ndaspect[0]), abs(ry*ndaspect[1]), 
        #             abs(rz*ndaspect[2])
        
        # Convert to screen coordinates. In screen x, only x and y have effect.
        # In screen y, all three dimensions have effect. The idea of the lines
        # below is to calculate the range on screen when that will fit the 
        # data under any rotation.
        rxs = (rx**2 + ry**2)**0.5
        rys = (rx**2 + ry**2 + rz**2)**0.5
        
        # Set zoom, depending on screen dimensions
        if w / h > 1:
            rxs *= w / h
            self._scale_factor = (1 / rxs) / 1.04  # 4% extra space
        else:
            self._scale_factor = (1 / rys) / 1.08  # 8% extra space
        
        # Update
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
        
        # todo: implement translation of center using shift+LMB
        
        if event.type == 'mouse_release':
            self._event_value = None  # Reset
        
        elif event.type == 'mouse_move':
            modifiers = event.mouse_event.modifiers
            
            if event.press_event is None:
                return
            
            if 1 in event.buttons and not modifiers:
                # todo: if shift/control is down, move center
                # Rotate
                if self._event_value is None:
                    self._event_value = self.azimuth, self.elevation
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                self.azimuth = self._event_value[0] - (p2 - p1)[0] * 0.5
                self.elevation = self._event_value[1] + (p2 - p1)[1] * 0.5
            
            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = self._scale_factor
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                d = p2 - p1
                self._scale_factor = self._event_value * _zoomfactor(d[1])
                self.view_changed()
            
            elif 2 in event.buttons and keys.CONTROL in modifiers:
                # Change fov
                if self._event_value is None:
                    self._event_value = self._fov
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                d = p2 - p1
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
    
    Parameters
    ----------
    fov : float
        Field of view. Default 60.0 (which corresponds more or less
        with the human eye).
    parent : Node
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    
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
    
    def __init__(self, **kwargs):
        
        # Position of the camera
        self._view_loc = 0, 0, 0
        
        # Motion speed vector
        self._speed = np.zeros((6,), 'float64')
        
        # Acceleration and braking vectors, set from keyboard
        self._brake = np.zeros((6,), 'uint8')  # bool-ish
        self._acc = np.zeros((6,), 'float64')
        
        # Init rotations
        self._auto_roll = True  # Whether to roll to make Z up
        self._rotation1 = Quaternion()  # The total totation
        self._rotation2 = Quaternion()  # The delta yaw and pitch rotation
        
        PerspectiveCamera.__init__(self, **kwargs)
        
        # Relative rotation and translation depending on size of scene
        speed_angle = 0.5*self._fov*math.pi/180
        self._speed_rot = math.sin(speed_angle)
        self._speed_trans = math.cos(speed_angle)
        
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
    
    def _reset(self):
        """ Reset the view.
        """
        
#         # Reset daspect from user-given daspect
#         if self.axes:
#             self._daspect = self.axes._daspect
        viewbox = self._ref_viewbox()
        
        # Stop moving
        self._speed *= 0.0
        
        # Set orientation
        q1 = Quaternion.create_from_axis_angle(-100*math.pi/180, 1, 0, 0)
        q2 = Quaternion.create_from_axis_angle(0*math.pi/180, 0, 1, 0)
        q3 = Quaternion.create_from_axis_angle(45*math.pi/180, 0, 0, 1)
        #
        self._rotation1 = (q1 * q2 * q3).normalize()
        self._rotation2 = Quaternion()
        self._fov = 60.0
        speed_angle = 0.5 * self._fov * math.pi/180
        self._speed_rot = math.sin(speed_angle)
        self._speed_trans = math.cos(speed_angle)
        
        # Get window size (and store factor now to sync with resizing)
        w, h = viewbox.size
        w, h = float(w), float(h)
        self._windowSizeFactor = h / w
        
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
        
#         # If auto-scale is on, change daspect, x is the reference
#         if self.axes.daspectAuto:
#             self._SetDaspect(rx/ry, 1, 0)
#             self._SetDaspect(rx/rz, 2, 0)
        
#         # Correct for normalized daspect
#         ndaspect = self.daspectNormalized
#         rx, ry, rz = abs(rx*ndaspect[0]), abs(ry*ndaspect[1]), 
#                      abs(rz*ndaspect[2])
        
        # Do not convert to screen coordinates. This camera does not need
        # to fit everything on screen, but we need to estimate the scale
        # of the data in the scene.
        
        # Set scale, depending on data range
        self._scale_factor = min(1/rx, 1/ry, 1/rz)
        
        # Set initial position to a corner of the scene
        #self._view_loc = x1, y1, z1
        margin = np.mean([rx, ry, rz]) * 0.1
        self._view_loc = x1 - margin, y1 - margin, z1 + margin
        
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
        rel_speed = 0.005
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
            #ndaspect = self.daspectNormalized
            #dv = Point([1.0/d for d in ndaspect])
            dv = np.array((1.0, 1.0, 1.0))
            #
            vf = pf * dv * rel_speed * self._speed_trans / self._scale_factor
            vr = pr * dv * rel_speed * self._speed_trans / self._scale_factor
            vu = pu * dv * rel_speed * self._speed_trans / self._scale_factor
            direction = vf, vr, vu
            
            # Set position
            self._view_loc = np.array(self._view_loc, dtype='float32')
            self._view_loc += (self._speed[0] * direction[0] + 
                               self._speed[1] * direction[1] +
                               self._speed[2] * direction[2])
        
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
                vec[dim-1] = val
    
    def view_mouse_event(self, event):
        
        viewbox = self._viewboxes[0]  # event.viewbox  
        
        # A bit awkward way to connect to our canvas; we need event
        # object to get a reference to the canvas
        if not self._key_events_bound:
            self._key_events_bound = True
            event.canvas.events.key_press.connect(self.view_key_event)
            event.canvas.events.key_release.connect(self.view_key_event)
        
        if event.handled or not self.interactive:
            return
        
        if event.type == 'mouse_wheel':
            # Move forward / backward
            self._speed[0] += 0.5 * event.delta[1]
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
            w, h = viewbox.size
            
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
        tr.translate(self._view_loc)


#class ArcballCamera(PerspectiveCamera):
#    pass


#class FirstPersonCamera(PerspectiveCamera):
#    pass
