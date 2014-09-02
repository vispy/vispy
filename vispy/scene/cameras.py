# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
A brief explanation of how cameras work 
---------------------------------------

A Camera is responsible for setting the transform of a SubScene object such 
that a certain part of the scene is mapped to the bounding rectangle of the 
ViewBox. 

The view of a camera is determined by its transform (that it has as
being an entity) and its projection. The former is essentially the
position and orientation of the camera, the latter determines field of
view and any non-linear transform (such as perspective).

"""
from __future__ import division

import numpy as np

from .entity import Entity
from ..geometry import Rect
from .transforms import (STTransform, PerspectiveTransform, NullTransform,
                         AffineTransform)


def make_camera(cam_type, *args, **kwds):
    """ Factory function for creating new cameras. 
    
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
    cam_types = {
        None: BaseCamera,
        'panzoom': PanZoomCamera,
        'turntable': TurntableCamera,
    }
    
    try: 
        return cam_types[cam_type](*args, **kwds)
    except KeyError:
        raise KeyError('Unknown camera type "%s". Options are: %s' % 
                       (cam_type, cam_types.keys()))


class BaseCamera(Entity):
    """ Camera describes the perspective from which a ViewBox views its 
    subscene, and the way that user interaction affects that perspective.
    
    Most functionality is implemented in subclasses. This base class has
    no user interaction and causes the subscene to use the same coordinate
    system as the ViewBox.

    Parameters
    ----------
    parent : Entity
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, **kwargs):
        self._viewbox = None
        self._interactive = True
        super(BaseCamera, self).__init__(**kwargs)
        self.transform = NullTransform()

    @property
    def interactive(self):
        """ Boolean describing whether the camera should enable or disable
        user interaction.
        """
        return self._interactive
    
    @interactive.setter
    def interactive(self, b):
        self._interactive = b

    @property
    def viewbox(self):
        """ The ViewBox that this Camera is attached to.        
        """
        return self._viewbox
    
    @viewbox.setter
    def viewbox(self, vb):
        if self._viewbox is not None:
            self.disconnect()
        self._viewbox = vb
        if self._viewbox is not None:
            self.connect()
            self.parent = vb.scene
        self._update_transform()
    
    def connect(self):
        self._viewbox.events.mouse_press.connect(self.view_mouse_event)
        self._viewbox.events.mouse_release.connect(self.view_mouse_event)
        self._viewbox.events.mouse_move.connect(self.view_mouse_event)
        self._viewbox.events.mouse_wheel.connect(self.view_mouse_event)
        self._viewbox.events.resize.connect(self.view_resize_event)
    
    def disconnect(self):
        self._viewbox.events.mouse_press.disconnect(self.view_mouse_event)
        self._viewbox.events.mouse_release.disconnect(self.view_mouse_event)
        self._viewbox.events.mouse_move.disconnect(self.view_mouse_event)
        self._viewbox.events.mouse_wheel.disconnect(self.view_mouse_event)
        self._viewbox.events.resize.disconnect(self.view_resize_event)
    
    def view_mouse_event(self, event):
        """
        The ViewBox received a mouse event; update transform 
        accordingly.
        """
        pass
        
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
        self._scene_transform = tr
        if self.viewbox is not None:
            self.viewbox.scene.transform = self._scene_transform
            self.viewbox.update()

    
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
    parent : Entity
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, **kwargs):
        super(PanZoomCamera, self).__init__(**kwargs)
        self._rect = Rect((0, 0), (1, 1))  # visible range in scene
        self._invert = [False, True]
        self.transform = STTransform()
        
    def zoom(self, zoom, center):
        """ Zoom the view around a center point.
        
        Parameters
        ----------
        zoom : length-2 sequence
            The fraction to zoom the x and y axes.
        center : length-2 sequence
            The point (in the coordinate system of the scene) that will remain
            stationary in the ViewBox while zooming.
        """
        # TODO: would be nice if STTransform had a nice scale(s, center) 
        # method like AffineTransform.
        transform = (STTransform(translate=center) * 
                     STTransform(scale=zoom) * 
                     STTransform(translate=-center))
        
        self.rect = transform.map(self.rect)
        
    def pan(self, pan):
        """ Pan the view.
        
        Parameters
        ----------
        pan : length-2 sequence
            The distance to pan the view, in the coordinate system of the 
            scene.
        """
        self.rect = self.rect + pan

    def auto_zoom(self, visual=None, padding=0.1):
        """ Automatically configure the camera to fit a visual inside the
        visible region.
        """
        bx = visual.bounds('visual', 0)
        by = visual.bounds('visual', 1)
        bounds = self.rect
        if bx is not None:
            bounds.left = bx[0]
            bounds.right = bx[1]
        if by is not None:
            bounds.bottom = by[0]
            bounds.top = by[1]
            
        if padding != 0:
            pw = bounds.width * padding * 0.5
            ph = bounds.height * padding * 0.5
            bounds.left = bounds.left - pw
            bounds.right = bounds.right + pw
            bounds.top = bounds.top + ph
            bounds.bottom = bounds.bottom - ph
        self.rect = bounds

    @property
    def rect(self):
        """ The rectangular border of the ViewBox visible area, expressed in
        the coordinate system of the scene.
        
        By definition, the +y axis of this rect is opposite the +y axis of the
        ViewBox. 
        """
        return self._rect
        
    @rect.setter
    def rect(self, args):
        """
        Set the bounding rect of the visible area in the subscene. 
        
        By definition, the +y axis of this rect is opposite the +y axis of the
        ViewBox. 
        """
        if isinstance(args, tuple):
            self._rect = Rect(*args)
        else:
            self._rect = Rect(args)
        self._update_transform()

    @property 
    def invert_y(self):
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
        self._update_transform()
        
    def view_resize_event(self, event):
        self._update_transform()

    def view_mouse_event(self, event):
        """
        The SubScene received a mouse event; update transform 
        accordingly.
        """
        if event.handled or not self.interactive:
            return
        
        if event.type == 'mouse_wheel':
            scale = 1.1 ** -event.delta[1]
            center = self._scene_transform.imap(event.pos[:2])
            self.zoom((scale, scale), center)
            event.handled = True
            
        elif event.type == 'mouse_move':
            if 1 in event.buttons:
                p1 = np.array(event.last_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1s = self._scene_transform.imap(p1)
                p2s = self._scene_transform.imap(p2)
                self.pan(p1s-p2s)
                event.handled = True
            elif 2 in event.buttons:
                # todo: just access the original event position, rather
                # than mapping to the viewbox and back again.
                p1 = np.array(event.last_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1c = event.map_to_canvas(p1)[:2]
                p2c = event.map_to_canvas(p2)[:2]
                
                scale = 1.03 ** ((p1c-p2c) * np.array([1, -1]))
                center = self._scene_transform.imap(event.press_event.pos[:2])
                
                self.zoom(scale, center)
                event.handled = True
        
        if event.handled:
            self._update_transform()

    def _update_transform(self):
        if self.viewbox is None:
            return
        
        vbr = self.viewbox.rect.flipped(x=self._invert[0], y=self._invert[1])
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
    mode : str
        Perspective mode, either 'ortho' or 'perspective'.
    fov : float
        Field of view.
    width : float
        Width.
    parent : Entity
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, mode='ortho', fov=60., width=10., **kwargs):
        # projection transform and associated options
        self._projection = PerspectiveTransform()
        self._mode = None
        self._fov = None
        self._width = None

        super(PerspectiveCamera, self).__init__(**kwargs)

        self.mode = mode
        self.fov = fov
        self.width = width
        
        # camera transform
        self.transform = AffineTransform()
        
    @property
    def mode(self):
        """ Describes the current projection mode of the camera. 
        
        May be 'ortho' or 'perspective'. In orthographic mode, objects appear 
        to have constant size regardless of their distance from the camera.
        In perspective mode, objects appear smaller as they are farther from 
        the camera.
        """
        return self._mode
    
    @mode.setter
    def mode(self, mode):
        if mode == 'ortho':
            self._near = -1e3
        elif mode == 'perspective':
            self._near = 1e-2
        else:
            raise ValueError('Accepted modes are "ortho" and "perspective".')
        self._far = 1e6
        self._mode = mode
        
        self._update_transform()
        
    @property
    def fov(self):
        """ Field-of-view angle of the camera when in perspective mode.
        """
        return self._fov
    
    @fov.setter
    def fov(self, fov):
        if fov < 0 or fov >= 180:
            raise ValueError("fov must be between 0 and 180.")
        self._fov = fov
        self._update_transform()
        
    @property
    def width(self):
        """ Width of the visible region when in orthographic mode.
        """
        return self._width
    
    @width.setter
    def width(self, width):
        self._width = width
        self._update_transform()
        
    def view_resize_event(self, event):
        self._update_transform()
    
    def _update_transform(self, event=None):
        if self.viewbox is None:
            return
        
        # configure projection transform
        if self.mode == 'ortho': 
            self.set_ortho()
        elif self.mode == 'perspective':
            self.set_perspective()
        else:
            raise ValueError("Unknown projection mode '%s'" % self.mode)
        
        # assemble complete transform mapping to viewbox bounds
        unit = [[-1, 1], [1, -1]]
        vrect = [[0, 0], self.viewbox.size]
        viewbox_tr = STTransform.from_mapping(unit, vrect)
        proj_tr = self._projection
        cam_tr = self.entity_transform(self.viewbox.scene)
        
        tr = viewbox_tr * proj_tr * cam_tr
        self._set_scene_transform(tr)

    def set_perspective(self):
        """ Set perspective projection matrix.
        """
        vbs = self.viewbox.size
        ar = vbs[0] / vbs[1]
        self._projection.set_perspective(self.fov, ar, self._near, self._far)

    def set_ortho(self):
        """ Set orthographic projection matrix.
        """
        vbs = self.viewbox.size
        w = self.width / 2.
        h = w * (vbs[1] / vbs[0])
        self._projection.set_ortho(-w, w, -h, h, self._near, self._far)


class TurntableCamera(PerspectiveCamera):
    """ 3D camera class that orbits around a center point while maintaining a
    fixed vertical orientation.

    Parameters
    ----------
    elevation : float
        Elevation in degrees.
    azimuth : float
        Azimuth in degrees.
    distance : float
        Distance away from the center.
    center : array-like
        3-element array defining the center point.
    parent : Entity
        The parent of the camera.
    name : str
        Name used to identify the camera in the scene.
    """
    def __init__(self, elevation=30., azimuth=30.,
                 distance=10., center=(0, 0, 0), up='z', **kwds):
        super(TurntableCamera, self).__init__(**kwds)
        self.elevation = elevation
        self.azimuth = azimuth
        self.distance = distance
        self.center = center
        self.up = up
        self._update_camera_pos()
    
    @property
    def elevation(self):
        """ The angle of the camera in degrees above the horizontal (x, z) 
        plane.
        """
        return self._elevation

    @elevation.setter
    def elevation(self, elev):
        self._elevation = elev
        self._update_transform()
    
    @property
    def azimuth(self):
        """ The angle of the camera in degrees around the y axis. An angle of
        0 places the camera within the (y, z) plane.
        """
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azim):
        self._azimuth = azim
        self._update_transform()
    
    @property
    def distance(self):
        """ The distance from the camera to its center point.
        """
        return self._distance

    @distance.setter
    def distance(self, dist):
        self._distance = dist
        self._update_transform()
    
    @property
    def center(self):
        """ The position of the turntable center. This is the point around 
        which the camera orbits.
        """
        return self._center

    @center.setter
    def center(self, center):
        self._center = center
        self._update_transform()
    
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
        self._update_camera_pos()
        
    def view_mouse_event(self, event):
        """
        The viewbox received a mouse event; update transform 
        accordingly.
        """
        if event.handled or not self.interactive:
            return
        
        if event.type == 'mouse_wheel':
            s = 1.1 ** -event.delta[1]
            if self.mode == 'ortho':
                self.width *= s
            else:
                self.fov = np.clip(self.fov * s, 0, 179)
            self._update_camera_pos()
        
        elif event.type == 'mouse_move' and 1 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            p1c = event.map_to_canvas(p1)[:2]
            p2c = event.map_to_canvas(p2)[:2]
            d = p2c - p1c
            self.orbit(-d[0], d[1])

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
                tr.translate((0.0, 0.0, -self.distance))
                tr.rotate(self.elevation, (-1, 0, 0))
                tr.rotate(self.azimuth, (0, 1, 0))
            elif self.up == 'z':
                tr.rotate(90, (1, 0, 0))
                tr.translate((0.0, -self.distance, 0.0))
                tr.rotate(self.elevation, (-1, 0, 0))
                tr.rotate(self.azimuth, (0, 0, 1))
            else:
                raise ValueError('TurntableCamera.up must be "y" or "z".')
                
            tr.translate(-np.array(self.center))
        self._update_transform()


#class ArcballCamera(PerspectiveCamera):
#    pass


#class FirstPersonCamera(PerspectiveCamera):
#    pass
