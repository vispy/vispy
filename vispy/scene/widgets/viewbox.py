# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..transforms import STTransform, NullTransform
from .widget import Widget
from ..subscene import SubScene
from ...util.geometry import Rect


class ViewBox(Widget):
    """ Provides a rectangular window to which its subscene is rendered
    """

    def __init__(self, *args, **kwds):
        self._viewer = None
        
        Widget.__init__(self, *args, **kwds)

        # Background color of this viewbox. Used in glClear()
        self._bgcolor = (0.0, 0.0, 0.0, 1.0)

        # Init preferred method to provided a pixel grid
        self._preferred_clip_method = 'none'

        # Each viewbox has a scene widget, which has a transform that
        # represents the transformation imposed by camera.
        self._scene = SubScene()
        self._scene.parent = self
        
        # Viewer is a helper object that handles scene transformation
        # and user interaction.
        self.viewer = PanZoomViewer()

    @property
    def viewer(self):
        return self._viewer
    
    @viewer.setter
    def viewer(self, v):
        self._viewer = v
        v.viewbox = self

    @property
    def bgcolor(self):
        """ The background color of the scene. within the viewbox.
        """
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        # Check / convert
        value = [float(v) for v in value]
        if len(value) < 3:
            raise ValueError('bgcolor must be 3 or 4 floats.')
        elif len(value) == 3:
            value.append(1.0)
        elif len(value) == 4:
            pass
        else:
            raise ValueError('bgcolor must be 3 or 4 floats.')
        # Set
        self._bgcolor = tuple(value)

    @property
    def scene(self):
        """ The root entity of the subscene of this viewbox. This entity
        takes care of the transformation imposed by the camera of the
        viewbox.
        """
        return self._scene

    def add(self, entity):
        """ Add an Entity to the scene for this ViewBox. 
        
        This is a convenience method equivalent to 
        `entity.add_parent(viewbox.scene)`
        """
        entity.add_parent(self.scene)

    @property
    def preferred_clip_method(self):
        """ The preferred way to clip the boundaries of the viewbox.

        There are three possible ways that the viewbox can perform
        clipping:

        * 'none' - do not perform clipping. The default for now.
        * 'fragment' - clipping in the fragment shader TODO
        * 'viewport' - use glViewPort to provide a clipped sub-grid
          onto the parent pixel grid, if possible.
        * 'fbo' - use an FBO to draw the subscene to a texture, and
          then render the texture in the parent scene.

        Restrictions and considerations
        -------------------------------

        The 'viewport' method requires that the transformation (from
        the pixel grid to this viewbox) is translate+scale only. If
        this is not the case, the method falls back to the default.

        The 'fbo' method is convenient when the result of the viewbox
        should be reused. Otherwise the overhead can be significant and
        the image can get slightly blurry if the transformations do
        not match.

        It is possible to have a graph with multiple stacked viewboxes
        which each use different methods (subject to the above
        restrictions).

        """
        return self._preferred_clip_method

    @preferred_clip_method.setter
    def preferred_clip_method(self, value):
        valid_methods = ('none', 'fragment', 'viewport', 'fbo')
        if value not in valid_methods:
            t = 'preferred_clip_method should be in %s' % str(valid_methods)
            raise ValueError((t + ', not %r') % value)
        self._preferred_clip_method = value

    def draw(self, event):
        """ Draw the viewbox.

        This does not really draw *this* object, but prepare for drawing
        our the subscene. In particular, here we calculate the transform
        needed to project the subscene in our viewbox rectangle. Also
        we handle setting a viewport if requested.
        """
        
        # todo: we could consider including some padding
        # so that we have room *inside* the viewbox to draw ticks and stuff
        
        # -- Calculate resolution
        
        # Get current transform and calculate the 'scale' of the viewbox
        size = self.size
        transform = event.full_transform
        p0, p1 = transform.map((0, 0)), transform.map(size)
        res = (p1 - p0)[:2]
        res = abs(res[0]), abs(res[1])

        # Set resolution (note that resolution can be non-integer)
        self._resolution = res
        
        # -- Set the viewbox_transform 
        
        # Map our resolution in pixels to our size
        mapfrom = (0, 0), res
        mapto = (0, 0), size
        self.scene.viewbox_transform = STTransform.from_mapping(mapfrom, mapto)
        
        # -- Get user clipping preference

        prefer = self.preferred_clip_method
        assert prefer in ('none', 'fragment', 'viewport', 'fbo')
        viewport, fbo = None, None

        if prefer == 'none':
            pass
        elif prefer == 'fragment':
            raise NotImplementedError('No fragment shader clipping yet.')
        elif prefer == 'viewport':
            viewport = self._prepare_viewport(event)
        elif prefer == 'fbo':
            fbo = self._prepare_fbo(event)

        # -- Draw
        super(ViewBox, self).draw(event)

        event.push_viewbox(self)

        if fbo:
            # Ask the canvas to activate the new FBO
            offset = event.full_transform.map((0, 0))[:2]
            size = event.full_transform.map(self.size)[:2] - offset
            
            event.push_fbo(fbo, offset, size)
            
            # Clear bg color (handy for dev)
            from ...gloo import gl
            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            # Process childen
            self.scene.draw(event)
            # Pop FBO and now draw the result
            event.pop_fbo()
            gl.glDisable(gl.GL_CULL_FACE)
            self._myprogram.draw(gl.GL_TRIANGLE_STRIP)

        elif viewport:
            # Push viewport, draw, pop it
            event.push_viewport(viewport)
            try:
                self.scene.draw(event)
            finally:
                event.pop_viewport()

        else:
            # Just draw
            # todo: invoke fragment shader clipping
            self.scene.draw(event)

        event.pop_viewbox()
        
    def _prepare_viewport(self, event):
        p1 = event.map_to_fb((0, 0))
        p2 = event.map_to_fb(self.size)
        return p1[0], p1[1], p2[0]-p1[0], p2[1]-p1[1]

    def _prepare_fbo(self, event):
        """ Draw the viewbox via an FBO. This method can be applied
        in any situation, regardless of the transformations to this
        viewbox.

        TODO:
        Right now, this implementation create a program, texture and FBO
        on *each* draw, because it does not work otherwise. This is probably
        a bug in gloo that prevents using two FBO's / programs at the same
        time.

        Also, we use plain gloo and calculate the transformation
        ourselves, assuming 2D only. Eventually we should just use the
        transform of self. I could not get that to work, probably
        because I do not understand the component system yet.
        """

        from vispy.gloo import gl
        from vispy import gloo

        render_vertex = """
            attribute vec3 a_position;
            attribute vec2 a_texcoord;
            varying vec2 v_texcoord;
            void main()
            {
                gl_Position = vec4(a_position, 1.0);
                v_texcoord = a_texcoord;
            }
        """

        render_fragment = """
            uniform sampler2D u_texture;
            varying vec2 v_texcoord;
            void main()
            {
                vec4 v = texture2D(u_texture, v_texcoord);
                gl_FragColor = vec4(v.rgb, 1.0);
            }
        """

        # todo: don't do this on every draw
        if True:
            # Create program
            self._myprogram = gloo.Program(render_vertex, render_fragment)
            # Create texture
            self._tex = gloo.Texture2D(shape=(10, 10, 4), dtype=np.uint8)
            self._tex.interpolation = gl.GL_LINEAR
            self._myprogram['u_texture'] = self._tex
            # Create texcoords and vertices
            # Note y-axis is inverted here because the viewbox coordinate
            # system has origin in the upper-left, but the image is rendered
            # to the framebuffer with origin in the lower-left.
            texcoord = np.array([[0, 1], [1, 1], [0, 0], [1, 0]],
                                dtype=np.float32)
            position = np.zeros((4, 3), np.float32)
            self._myprogram['a_texcoord'] = gloo.VertexBuffer(texcoord)
            self._myprogram['a_position'] = self._vert = \
                gloo.VertexBuffer(position)

        # Get fbo, ensure it exists
        fbo = getattr(self, '_fbo', None)
        if True:  # fbo is None:
            self._fbo = 4
            self._fbo = fbo = gloo.FrameBuffer(self._tex,
                                               depth=gloo.DepthBuffer((10,
                                                                       10)))

        # Set texture coords to make the texture be drawn in the right place
        # Note that we would just use -1..1 if we would use a Visual.
        coords = [[0, 0], [self.size[0], self.size[1]]]
        
        transform = event.render_transform  # * self.scene.viewbox_transform
        coords = transform.map(coords)
        x1, y1, z = coords[0][:3]
        x2, y2, z = coords[1][:3]
        vertices = np.array([[x1, y1, z], [x2, y1, z],
                             [x1, y2, z], [x2, y2, z]],
                            np.float32)
        self._vert.set_data(vertices)

        # Set fbo size (mind that this is set using shape!)
        resolution = [int(i+0.5) for i in self._resolution]  # set in draw()
        shape = resolution[1], resolution[0]
        fbo.color_buffer.resize(shape+(4,))
        fbo.depth_buffer.resize(shape)

        return fbo

    def on_mouse_move(self, event):
        if self._viewer is not None:
            self._viewer.mouse_event(event)
        
    def on_rect_change(self, event):
        if self._viewer is not None:
            self._viewer.resize_event(event)


class Viewer(object):
    """
    Helper class that handles setting the sub-scene transformation of a ViewBox
    and reacts to user input.
    """
    def __init__(self):
        self._viewbox = None
        self._transform = NullTransform()

    @property
    def viewbox(self):
        return self._viewbox
    
    @viewbox.setter
    def viewbox(self, vb):
        self._viewbox = vb
        self.update()
    
    @property
    def transform(self):
        """
        Transform to apply to the ViewBox's SubScene.
        """
        return self._transform
        
    @transform.setter
    def transform(self, tr):
        self._transform = tr
        self.update()
        
    def mouse_event(self, event):
        """
        The SubScene received a mouse event; update transform 
        accordingly.
        """
        pass
        
    def resize_event(self, event):
        """
        The ViewBox was resized; update the transform accordingly.
        """
        pass
        
    def update(self):
        """
        Set the scene transform to match the Viewer's transform.
        """
        if self.viewbox is not None:
            self.viewbox.scene.transform = self.transform
        
    
class PanZoomViewer(Viewer):
    """
    Viewer implementing 2D pan/zoom mouse interaction. Primarily intended for
    displaying plot data.
    """
    def __init__(self):
        super(PanZoomViewer, self).__init__()
        self._rect = Rect((0, 0), (1, 1))  # visible range in scene
        self._transform = STTransform()
        self._mouse_enabled = True
        
    @property
    def mouse_enabled(self):
        return self._mouse_enabled
    
    @mouse_enabled.setter
    def mouse_enabled(self, b):
        self._mouse_enabled = b
    
    def mouse_event(self, event):
        """
        The SubScene received a mouse event; update transform 
        accordingly.
        """
        if event.handled or not self._mouse_enabled:
            return
        
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            p1s = self.transform.imap(p1)
            p2s = self.transform.imap(p2)
            self.rect = self.rect + (p1s-p2s)
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            p1c = event.map_to_canvas(p1)[:2]
            p2c = event.map_to_canvas(p2)[:2]
            s = 1.03 ** ((p1c-p2c) * np.array([1, -1]))
            center = self.transform.imap(event.press_event.pos[:2])
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            transform = (STTransform(translate=center) * 
                         STTransform(scale=s) * 
                         STTransform(translate=-center))
            
            self.rect = transform.map(self.rect)
            event.handled = True
        
        if event.handled:
            self.update()

    def resize_event(self, event):
        self.update()

    @property
    def rect(self):
        return self._rect
        #return self.transform.imap(self.viewbox.rect)
        
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
        self.update()
        
    def update(self):
        if self.viewbox is not None:
            vbr = self.viewbox.rect.flipped(y=True, x=False)
            self.transform.set_mapping(self.rect, vbr)
        super(PanZoomViewer, self).update()

        
class CameraViewer(Viewer):
    """
    Viewer that generates its transform from a Camera Entity placed inside the 
    scene.
    """
    def __init__(self, viewbox):
        super(CameraViewer, self).__init__(viewbox)
        self._camera = None
        self.camera = OrthoCamera(self)

    @property
    def camera(self):
        """ The camera associated with this viewbox. Can be None if there
        are no cameras in the scene.
        """
        return self._camera

    @camera.setter
    def camera(self, cam):
        # convenience: set parent if it's an orphan
        if not cam.parents:
            cam.parents = self
        # Test that self is a parent of the camera
        object = cam
        while object is not None:
            # todo: ignoring multi-parenting here, we need Entity.isparent()
            object = object.parents[0]
            if isinstance(object, SubScene):
                break
        if object is not self:
            raise ValueError('Given camera is not in the scene itself.')
        # Set and (dis)connect events
#         if self._camera is not None:
#             self._camera.events.update.disconnect(self._camera_update)
        self._camera = cam
#         cam.events.update.connect(self._camera_update)

    def update(self):
        if self.viewbox is not None:
            pass
            # TODO: set transform from inverse camera transform
        super(PanZoomViewer, self).update()
    