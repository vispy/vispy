# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy.visuals.transforms import STTransform




class PanZoomTransform(STTransform):
    def __init__(self, canvas=None, **kwargs):
        self.attach(canvas)
        STTransform.__init__(self, **kwargs)
        
    def attach(self, canvas):
        """ Attach this tranform to a canvas """

        self._canvas = canvas

        canvas.connect(self.on_resize)
        canvas.connect(self.on_mouse_wheel)
        canvas.connect(self.on_mouse_move)
        
    #def on_resize(self, event):
        #""" Resize event """

        #self._width = float(event.size[0])
        #self._height = float(event.size[1])
        #aspect = self._width/self._height
        #if aspect > 1.0:
            #self._canvas_aspect = np.array([1.0/aspect, 1.0])
        #else:
            #self._canvas_aspect = np.array([1.0, aspect/1.0])

        ## Update zoom level
        #self.zoom = self._zoom


    def on_mouse_move(self, event):
        """ Drag """

        if not event.is_dragging:
            return

        x, y = event.pos
        dx = +2*((x-event.last_event.pos[0]) / self._width)
        dy = -2*((y-event.last_event.pos[1]) / self._height)

        self.pan += dx,dy
        self._canvas.update()

    def on_mouse_move(self, event):
        if event.is_dragging:
            dxy = event.pos - event.last_event.pos
            button = event.press_event.button

            if button == 1:
                self.move(dxy)
            elif button == 2:
                center = event.press_event.pos
                self.zoom(np.exp(dxy * (0.01, -0.01)), center)

    def on_mouse_wheel(self, event):
        self.zoom(np.exp(event.delta * (0.01, -0.01)), event.pos)









class PanZoom(object):

    """
    Pan & Zoom transform

    The panzoom transform allow to translate and scale an object in the window
    space coordinate (2D). This means that whatever point you grab on the
    screen, it should remains under the mouse pointer. Zoom is realized using
    the mouse scroll and is always centered on the mouse pointer.

    The transform is connected to the following events:

    * resize (update)
    * mouse_scroll (zoom)
    * mouse_grab (pan)

    You can also control programatically the transform using:

    * aspect: control the aspect ratio of the whole scene
    * pan   : translate the scene to the given 2D coordinates
    * zoom  : set the zoom level (centered at current pan coordinates)
    * zmin  : minimum zoom level
    * zmax  : maximum zoom level
    """

    glsl = """
    uniform vec2 u_zoom;
    uniform vec2 u_pan;
    vec4 transform(vec3 position)
    {
        return vec4(u_zoom*position.xy + u_pan, position.z, 1.0);
    }
    """

    def __init__(self, aspect=1.0, pan=(0.0, 0.0), zoom=1.0,
                 zmin=0.01, zmax=100.0):
        """
        Initialize the transform.

        Parameters
        ----------

        aspect : float (default is None)
           Indicate what is the aspect ratio of the object displayed. This is
           necessary to convert pixel drag move in oject space coordinates.

        pan : float, float (default is 0,0)
           Initial translation

        zoom : float, float (default is 1)
           Initial zoom level

        zmin : float (default is 0.01)
           Minimum zoom level

        zmax : float (default is 1000)
           Maximum zoom level
        """

        self._aspect = aspect
        self._pan = np.array(pan)
        self._zoom = zoom
        self._zmin = zmin
        self._zmax = zmax

        # Canvas this transform is attached to
        self._canvas = None
        self._canvas_aspect = np.ones(2)
        self._width = 1
        self._height = 1

        # Programs using this transform
        self._u_pan = pan
        self._u_zoom = np.array([zoom, zoom])
        self._programs = []

    @property
    def is_attached(self):
        """ Whether transform is attached to a canvas """

        return self._canvas is not None

    @property
    def aspect(self):
        """ Aspect (width/height) """

        return self._aspect

    @aspect.setter
    def aspect(self, value):
        """ Aspect (width/height) """

        self._aspect = value

    @property
    def pan(self):
        """ Pan translation """

        return self._pan

    @pan.setter
    def pan(self, value):
        """ Pan translation """

        self._pan = np.asarray(value)
        self._u_pan = self._pan
        for program in self._programs:
            program["u_pan"] = self._u_pan

    @property
    def zoom(self):
        """ Zoom level """

        return self._zoom

    @zoom.setter
    def zoom(self, value):
        """ Zoom level """

        self._zoom = max(min(value, self._zmax), self._zmin)
        if not self.is_attached:
            return

        aspect = 1.0
        if self._aspect is not None:
            aspect = self._canvas_aspect * self._aspect

        self._u_zoom = self._zoom * aspect
        for program in self._programs:
            program["u_zoom"] = self._u_zoom

    @property
    def zmin(self):
        """ Minimum zoom level """

        return self._zmin

    @zmin.setter
    def zmin(self, value):
        """ Minimum zoom level """

        self._zmin = min(value, self._zmax)

    @property
    def zmax(self):
        """ Maximal zoom level """

        return self._zmax

    @zmax.setter
    def zmax(self, value):
        """ Maximal zoom level """

        self._zmax = max(value, self._zmin)

    def on_resize(self, event):
        """ Resize event """

        self._width = float(event.size[0])
        self._height = float(event.size[1])
        aspect = self._width / self._height
        if aspect > 1.0:
            self._canvas_aspect = np.array([1.0 / aspect, 1.0])
        else:
            self._canvas_aspect = np.array([1.0, aspect / 1.0])

        # Update zoom level
        self.zoom = self._zoom

    def on_mouse_move(self, event):
        """ Drag """

        if not event.is_dragging:
            return

        x, y = event.pos
        dx = +2 * ((x - event.last_event.pos[0]) / self._width)
        dy = -2 * ((y - event.last_event.pos[1]) / self._height)

        self.pan += dx, dy
        self._canvas.update()

    def on_mouse_wheel(self, event):
        """ Zoom """

        x, y = event.pos
        dx, dy = event.delta
        dx /= 10.0
        dy /= 10.0

        # Normalize mouse coordinates and invert y axis
        x = x / (self._width / 2.) - 1.0
        y = 1.0 - y / (self._height / 2.0)

        zoom = min(max(self._zoom * (1.0 + dy), self._zmin), self._zmax)
        ratio = zoom / self.zoom
        xpan = x - ratio * (x - self.pan[0])
        ypan = y - ratio * (y - self.pan[1])
        self.zoom = zoom
        self.pan = xpan, ypan
        self._canvas.update()

    def add(self, programs):
        """ Attach programs to this tranform """

        if not isinstance(programs, (list, tuple)):
            programs = [programs]

        for program in programs:
            self._programs.append(program)
            program["u_zoom"] = self._u_zoom
            program["u_pan"] = self._u_pan

    def attach(self, canvas):
        """ Attach this tranform to a canvas """

        self._canvas = canvas
        self._width = float(canvas.size[0])
        self._height = float(canvas.size[1])

        aspect = self._width / self._height
        if aspect > 1.0:
            self._canvas_aspect = np.array([1.0 / aspect, 1.0])
        else:
            self._canvas_aspect = np.array([1.0, aspect / 1.0])

        aspect = 1.0
        if self._aspect is not None:
            aspect = self._canvas_aspect * self._aspect
        self._u_zoom = self._zoom * aspect

        canvas.connect(self.on_resize)
        canvas.connect(self.on_mouse_wheel)
        canvas.connect(self.on_mouse_move)
