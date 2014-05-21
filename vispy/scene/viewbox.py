# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .entity import Entity
from .transforms import STTransform, NullTransform, PerspectiveTransform
from ..util.event import Event


from .visuals import Visual

class Widget(Visual):
    """ A widget takes up a rectangular space, intended for use in 
    a 2D pixel coordinate frame.
    
    The widget is positioned using the transform attribute (as any
    entity), and its extend (size) is kept as a separate property.
    
    This is a simple preliminary version!
    """
    
    def __init__(self, *args, **kwargs):
        #Entity.__init__(self, *args, **kwargs)
        Visual.__init__(self, *args, **kwargs)
        self.events.add(rect_change=Event)
        self._size = 16, 16
        self.transform = STTransform()  # todo: TTransform (translate only)
    
    @property
    def pos(self):
        return tuple(self.transform.translate[:2])
    
    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        self.transform.translate = p[0], p[1], 0, 1
        self.events.rect_change()
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, s):
        assert isinstance(s, tuple)
        assert len(s) == 2
        self._size = s
        self.events.rect_change()


class ViewBox(Widget):
    """ Provides a rectangular pixel grid to which its subscene is rendered
    
    The viewbox defines a certain coordinate frame using a camera (which
    is an entity in the subscene itself). A viewbox also defines
    background color, lights, and has its own drawing system.
    
    The viewbox provides a rectangular pixel grid using one of three methods,
    see the docs of prefer_pixel_grid for more information.
    """
    
    def __init__(self, *args, **kwds):
        Widget.__init__(self, *args, **kwds)
        self._child_group = Entity(parents=[self])
        
        # Background color of this viewbox. Used in glClear()
        self._bgcolor = (0.0, 0.0, 0.0, 1.0)
        
        # Init preferred method to provided a pixel grid
        self._prefer_pixel_grid = 'viewport'
        
        # Each viewbox has a camera. Default is NDCCamera (i.e. null camera)
        self._camera = None
        self.camera = NDCCamera(self)
        
        # Initialize systems
        self._systems = {}
        self._systems['draw'] = DrawingSystem()
    
    
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
            # todo: ignoring multi-parentin here, we need Entity.isparent()
            object = object.parents[0]  
            if isinstance(object, ViewBox):
                break
        if object is not self:
            raise ValueError('Given camera is not in the scene of the ViewBox.')
        # Set and (dis)connect events
        if self._camera is not None:
            self._camera.events.update.disconnect(self._camera_update)
        self._camera = cam
        cam.events.update.connect(self._camera_update)
    
    def get_cameras(self):
        """ Get a list of all cameras that live in this scene.
        """
        def getcams(val):
            cams = []
            for entity in val:
                if isinstance(entity, Camera):
                    cams.append(entity)
                if isinstance(entity, ViewBox):
                    pass # Do not go into subscenes
                elif isinstance(entity, Entity):  # if, not elif!
                    cams.extend(getcams(entity))
            return cams
        return getcams(self)
    
    
    def _camera_update(self, event):
        self._child_group.transform = self.camera.transform.inverse()
        
    def add(self, entity):
        entity.add_parent(self._child_group)
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if event.press_event is None or not self.rect.contains(*event.press_event.pos[:2]):
            return
            
        self.camera.view_mouse_event(event)

#     def on_paint(self, event):
#         super(ViewBox, self).on_paint(event)
#         
#         r = self.rect.padded(self.margin)
#         r = event.framebuffer_transform.map(r).normalized()
#         event.push_viewport(r.left, r.bottom, r.width, r.height)
#         
#     def on_children_painted(self, event):
#         event.pop_viewport()
    
    def process_system(self, event, system_name):
        """ Process a system.
        """
        self._systems[system_name].process(event)
    
    
    @property
    def prefer_pixel_grid(self):
        """ The preferred way to provide a pixel grid
        
        There are three possible ways that the viewbox can provide a virtual
        rectangular (and clipped) pixel grid:
        
        * 'viewport' - use glViewPort to provide a clipped sub-grid
          onto the parent pixel grid.
        * 'transform' - calculate the transformation from the current
          pixel grid to this viewbox, and make that transformation part
          of the total transform of all sub-entities. Clipping is
          performed in the fragment shader TODO!
        * 'fbo' - use an FBO to draw the subscene to a texture, and
          then render the texture in the parent scene.
        
        Restrictions and considerations
        -------------------------------
        
        The 'viewport' and 'transform' methods require that the
        transformation (from the pixel grid to this viewbox) is
        translate+scale only. For the 'viewport' method, the dimensions
        must also be fully contained inside the parent pixel grid. If
        these restrictions are not met, the 'fbo' method is used.
        
        The 'fbo' method *always* works, even if the parent viewbox
        uses a 3D camera. Further it allows using any resolution, and
        reusing of the resulting render image. Although the 'fbo' method
        is clearly the most flexible, the other methods are more
        efficient, especially if a large number of subplots are used.
        
        The 'transform' method should allow creating collections that
        span multiple viewboxes.
        
        It is possible to have a graph with multiple stacked viewboxes
        which each use different methods (subject to the above
        restrictions).
        
        """
        return self._prefer_pixel_grid
    
    @prefer_pixel_grid.setter
    def prefer_pixel_grid(self, value):
        if value not in ('viewport', 'transform', 'fbo'):
            t = 'prefer_pixel_grid should be "viewport", "transform" or "fbo"'
            raise ValueError(t + ', not %r' % value)
        self._prefer_pixel_grid = value
    
    
    def paint(self, event):
        """ Paint the viewbox. 
        
        This does not really draw *this* object, but prepare for drawing
        our childen to the virtual canvas that this viewbox represents.
        Then the drawing system is invoked to draw the children
        themselves. 
        """
        
        # Is this the root viewbox?
        is_root = event.canvas.root is self
        
        # Get whether the transform to here is translate-scale only
        is_ts_only = False
        if isinstance(self._total_transform, (NullTransform, STTransform)):
            is_ts_only = True
        
        # Get user preference
        prefer = self.prefer_pixel_grid
        assert prefer in ('viewport', 'transform', 'fbo')
        
        # Do what a viewbox does, in one of three ways ...
        if is_root or (is_ts_only and prefer == 'viewport'):
            self._paint_viewport(event)
        elif is_ts_only and prefer == 'transform':
            self._paint_via_transform(event)
        else:
            self._paint_via_fbo(event)
    
    
    def _get_pixel_rect_assuming_st_transform(self, event):
        """ Get the pixel rectangle coordinates for this viewbox,
        assuming that we only have translation and scale with respect
        to the parent pixel grid.
        """
        
        if event.canvas.root is self:
            # Do not take transform into account if root; the root
            # can have a parent and a transform and a size with respect
            # to that parent. But we should ignore these here.
            transform = STTransform(translate=(-1.0, -1.0))
            size = 2.0, 2.0
        else:
            # Multiply with unit STTTransform in case total_transform is Null
            transform = self._total_transform2 * STTransform()
            size = self.size 
        
        # Calculate x, y and w, h
        tx, ty = transform.translate[:2]
        sx, sy = transform.scale[:2]
        res = event.resolution
        
        # Transform from NDC to viewport coordinates
        x = (1.0 + tx) * res[0] * 0.5
        y = (1.0 + ty) * res[1] * 0.5
        w = (size[0] * sx) * res[0] * 0.5
        h = (size[1] * sy) * res[1] * 0.5
        
        # Return rounded to integers
        return int(x+0.5), int(y+0.5), int(w+0.5), int(h+0.5)
    
    
    def _paint_viewport(self, event):
        """ Paint the viewbox via a viewport. This assumes that there
        are no transforms from the previous viewport to here, except
        for translation and scaling.
        
        This method for providing a rectangular pixel grid is the most
        straightforward and relatively efficient.
        """
        
        # Get viewport and resolution of parent pixel grid
        x, y, w, h = self._get_pixel_rect_assuming_st_transform(event)
        res = event.resolution
        
        # Check if we are inside the bounds of the parent pixel grid. 
        # If not, use transform method
        if x < 0 or y < 0: 
            return self._paint_via_transform(event)
        if (x+w) > res[0] or (y+h) > res[1]: 
            return self._paint_via_transform(event)
        
        # Process our children
        event.push_viewbox(self, (x, y, w, h))
        self.process_system(event, 'draw')  # invoke our drawing system
        event.pop_viewbox()
        # ... return to canvas, or drawing system that invoked us ...
    
    
    def _paint_via_transform(self, event):
        """ Paint the viewbox via a transform. This assumes that there
        are no transforms from the previous viewport to here, except
        for translation and scaling.
        
        This method for providing a rectangular pixel grid may be the
        most efficient, especially if many viewboxes are used, because
        there is no overhead for setting viewport and scisssors. Also,
        collection may "cross this viewbox". However, this method
        required an alternative clipping method (not yet implemented),
        e.g. in the fragment shader.
        """
    
        # Get viewport and resolution of parent pixel grid
        x, y, w, h = self._get_pixel_rect_assuming_st_transform(event)
        
        # Process our children
        event.push_viewbox(self, (x, y, w, h), use_transform=True)
        self.process_system(event, 'draw')  # invoke our drawing system
        event.pop_viewbox()
        # ... return to canvas, or drawing system that invoked us ...
    
    
    def _paint_via_fbo(self, event):
        """ Paint the viewbox via an FBO. This method can be applied
        in any situation, regardless of the transformations to this
        viewbox.
        
        This method for providing a rectangular pixel grid is the least
        efficient. One should use it when the above two methods cannot
        be used, or when the rendered image needs to be cached and/or
        reused.
        
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
            self._tex = gloo.Texture2D(shape=(10,10,4), dtype=np.uint8)
            self._tex.interpolation = gl.GL_LINEAR
            self._myprogram['u_texture'] = self._tex
            # Create texcoords and vertices
            texcoord = np.array([[0,0], [1,0], [0,1], [1,1]], dtype=np.float32)
            position = np.zeros((4,3), np.float32)
            self._myprogram['a_texcoord'] = gloo.VertexBuffer(texcoord)
            self._myprogram['a_position'] = self._vert = gloo.VertexBuffer(position)
        
        # Get fbo, ensure it exists
        fbo = getattr(self, '_fbo', None)
        if True:#fbo is None:
            self._fbo = 4
            self._fbo = fbo = gloo.FrameBuffer(self._tex, 
                                    depth=gloo.DepthBuffer((10,10)),
                                    )
        
        # todo: for now we assume scale-translate only!
        # Get viewport and resolution of parent pixel grid
        x, y, w, h = self._get_pixel_rect_assuming_st_transform(event)
        res = event.resolution
        # Set texture coords to make the texture be drawn in the right place
        x1, y1 = 2*x/res[0]-1, 2*y/res[1]-1
        x2, y2 = x1 + 2*w/res[0], y1 + 2*h/res[1]
        z = 0
        vertexes = np.array([[x1,y1,z], [x2,y1,z], [x1,y2,z], [x2,y2,z]], 
                            np.float32)
        self._vert.set_data(vertexes)
        
        # Set resolution of pixel grid that we provide (can be anything!)
        # We add one, to get a barely noticable mis-alignment, so that
        # interpolation kicks in and we clearly see that this is an FBO
        resolution = int(w+1), int(h+1)
        
        # Set fbo size (mind that this is set using shape!)
        shape = resolution[1], resolution[0]
        fbo.color_buffer.resize(shape+(4,))
        fbo.depth_buffer.resize(shape)
        
        # Select bg color (handy for dev)
        clrs = {'':(0.1, 0.1, 0.1), 
                'vb1':(0.2,0,0), 'vb11':(0.2,0,0.1), 'vb12':(0.2,0,0.2), 
                'vb2':(0,0.2,0), 'vb21':(0,0.2,0.1), 'vb22':(0,0.2,0.2)}
        clr = clrs['']  # clrs[getattr(self,'_name', '')]
        
        # Prepare viewbox
        rect = 0, 0, resolution[0], resolution[1]
        event.push_viewbox(self, rect, fbo=fbo)
        gl.glClearColor(clr[0], clr[1], clr[2], 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Process childen
        self.process_system(event, 'draw')  # invoke our drawing system
        # Revert
        #gl.glFlush()
        event.pop_viewbox()
        # Draw the result in the parent scene
        self._myprogram.draw(gloo.gl.GL_TRIANGLE_STRIP)
        # ... return to canvas, or drawing system that invoked us ...



class Document(Entity):
    """
    Box that represents the area of a rectangular document with 
    physical dimensions. 
    """
    def __init__(self, *args, **kwds):
        self._dpi = 100  # will be used to relate other units to pixels
        super(Document, self).__init__(*args, **kwds)
        
    @property
    def dpi(self):
        return self._dpi
    
    @dpi.setter
    def dpi(self, d):
        self._dpi = dpi
        # TODO: inform tree that resolution has changed..



class DrawingSystem(object):
    """ Simple implementation of a drawing engine. There is one system
    per viewbox.
    """
    
    def process(self, event):
        viewbox = event.viewbox
        root = event.canvas
        if not isinstance(viewbox, ViewBox):
            raise ValueError('DrawingSystem.draw expects a ViewBox instance.')
        
        # Get camera transforms
        self._camtransform = self._get_camera_transform(viewbox.camera)
        self._projection = viewbox.camera.get_projection(event)
        
        # Iterate over entities
        for entity in viewbox:
            self._process_entity(event, entity)
    
    
    def _process_entity(self, event, entity):
        from .visuals import Visual  # todo: import crap
        
        event.canvas._process_entity_count += 1
        
        # Push entity and set its total transform
        event.push_entity(entity)
        entity._total_transform = (event.transform_to_viewbox *
                                   self._projection * 
                                   self._camtransform * 
                                   event.transform_from_viewbox  
                                  ).simplify()
              
        # We multiply with NullTransform. This seems needed in some situation.
        # I am not exactly sure, but I suspect that if we don't, different
        # entities can share the transform object, causing problems.
        # todo: look into this              
        entity._total_transform = entity._total_transform * NullTransform()
        
        # Also a transform without the virtual viewport
        entity._total_transform2 = (self._projection * # todo: clean up
                                   self._camtransform * 
                                   event.transform_from_viewbox 
                                  ).simplify()
                                  
        if isinstance(entity, ViewBox):
            # If a viewbox, render the subscene (*this* drawing system
            # does not process its children)
            entity.paint(event)
        else:
            # Paint if it is a visual
            if isinstance(entity, Visual):
                entity.paint(event)
            # Processs children; recurse
            for sub_entity in entity:
                self._process_entity(event, sub_entity)
        
        event.pop_entity()

    
    def _get_camera_transform(self, camera):
        """ Calculate the transform from the camera to the viewbox.
        This is the inverse of the transform chain *to* the camera.
        """
        from .viewbox import ViewBox
        
        # Get total transform of the camera
        object = camera
        camtransform = object.transform
        
        while True:
            # todo: does it make sense to have a camera in a multi-path scene?
            object = object.parents[0]
            if object is None:
                break  # Root viewbox
            elif isinstance(object, ViewBox):
                break  # Go until the any parent ViewBox
            assert isinstance(object, Entity)
            if object.transform is not None:
                camtransform = camtransform * object.transform
        
        # Return inverse!
        return camtransform.inverse()


from . import transforms  # Needed by cameras


class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.
    
    Next to the normal transformation, a camera also defines a
    projection tranformation that defines the camera view. This can for
    instance be orthographic, perspective, log, polar, etc.
    """
    
    def __init__(self, parent=None):
        Entity.__init__(self, parent)
        
        # Can be orthograpic, perspective, log, polar, map, etc.
        # Default unit
        self._projection = transforms.NullTransform()
    
    
    def get_projection(self, event):
        """ Get the projection matrix. Should be overloaded by camera
        classes to define the projection of view.
        """
        return self._projection



class NDCCamera(Camera):
    """ Camera that presents a view on the world in normalized device
    coordinates (-1..1).
    """
    pass



class PixelCamera(Camera):
    """ Camera that presents a view on the world in pixel coordinates.
    The coordinates map directly to the viewbox coordinates. The origin
    is in the upper left.
    """
    def get_projection(self, event):
        w, h = event.resolution
#         from vispy.util import transforms as trans
#         projection = np.eye(4)
#         trans.scale(projection, 2.0/w, 2.0/h)
#         trans.translate(projection, -1, -1)
#         trans.scale(projection, 1, -1)  # Flip y-axis
#         #return transforms.AffineTransform(projection)
        trans = transforms.STTransform()
        # todo: flip back y-axis ?
        trans.scale = 2.0/w, 2.0/h  # Flip y-axis
        trans.translate = -1, -1
        return trans



class TwoDCamera(Camera):

    def __init__(self, parent=None):
        super(TwoDCamera, self).__init__(parent)
        self.transform = STTransform()

    ## xlim and ylim are convenience methods to set the view using limits
    #@property
    #def xlim(self):
        #x = self.transform[-1, 0]
        #dx = self.fov[0] / 2.0
        #return x - dx, x + dx

    #@property
    #def ylim(self):
        #y = self.transform[-1, 1]
        #dy = self.fov[1] / 2.0
        #return y - dy, y + dy

    #@xlim.setter
    #def xlim(self, value):
        #x = 0.5 * (value[0] + value[1])
        #rx = max(value) - min(value)
        #self.fov = rx, self.fov[1]
        #self.transform[-1, 0] = x

    #@ylim.setter
    #def ylim(self, value):
        #y = 0.5 * (value[0] + value[1])
        #ry = max(value) - min(value)
        #self.fov = self.fov[0], ry
        #self.transform[-1, 1] = y

    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event; 
        
        """
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)
            p2 = np.array(event.pos)
            self.transform = self.transform * STTransform(translate=p1-p2)
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            s = 0.97 ** ((p2-p1) * np.array([1, 1]))
            center = event.press_event.pos
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            self.transform = (self.transform *
                              STTransform(translate=center) * 
                              STTransform(scale=s) * 
                              STTransform(translate=-center))
            self.update()        
            event.handled = True


class PerspectiveCamera(Camera):
    """
    In progress.
    
    """
    def __init__(self, parent=None):
        super(PerspectiveCamera, self).__init__(parent)
        self.transform = PerspectiveTransform()
        # TODO: allow self.look to be derived from an Anchor
        self._perspective = {
            'look': np.array([0., 0., 0., 1.]),
            'near': 1e-6,
            'far': 1e6,
            'fov': 60,
            'top': np.array([0., 0., 1., 1.])
            }

    def _update_transform(self):
        # create transform based on look, near, far, fov, and top.
        self.transform.set_perspective(origin=(0,0,0), **self.perspective)
        
    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event; 
        
        """
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)
            p2 = np.array(event.pos)
            self.transform = self.transform * STTransform(translate=p1-p2)
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            s = 0.97 ** ((p2-p1) * np.array([1, -1]))
            center = event.press_event.pos
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            self.transform = (self.transform *
                              STTransform(translate=center) * 
                              STTransform(scale=s) * 
                              STTransform(translate=-center))
            self.update()        
            event.handled = True

