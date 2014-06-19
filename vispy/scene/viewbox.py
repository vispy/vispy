# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .entity import Entity
from .transforms import STTransform, NullTransform, PerspectiveTransform, ChainTransform
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
        self.transform = STTransform()  # todo: TTransform (translate only for widgets)
    
    @property
    def pos(self):
        return tuple(self.transform.translate[:2])
    
    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        self.transform.translate = p[0], p[1], 0, 0
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



class SubScene(Entity):
    """ A subscene with entities.
    
    A subscene can be a child of a Canvas or a ViewBox. It is a
    placeholder for the transform to make the sub scene appear as
    intended. It's transform cannot be mannually set, but its set
    automatically and is based on three components:
    
      * Viewbox transform: a scale and translation to make the subscene
        be displayed in the boundaries of the viewbox.
      * Projection transform: the camera projection, e.g. perspective
      * position transform: the inverse of the transform from this
        subscene to the camera. This takes care of position and
        orientation of the view.
    
    TODO: should camera, lights, etc. be properties of the subscene or the
    viewbox? I think of the scene. In that way canvas.root can simply
    be a subscene.
    """
    
    def __init__(self, parent=None):
        Entity.__init__(self, parent)
        
        # Each scene has a camera. Default is NDCCamera (i.e. null camera)
        self._camera = None
        self.camera = NDCCamera(self)
        
        self.viewbox_transform = NullTransform()
        
        # Initialize systems
        self._systems = {}
        self._systems['draw'] = DrawingSystem()
    
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
    
    def get_cameras(self):
        """ Get a list of all cameras that live in this scene.
        """
        def getcams(val):
            cams = []
            for entity in val:
                if isinstance(entity, Camera):
                    cams.append(entity)
                if isinstance(entity, SubScene):
                    pass # Do not go into subscenes
                elif isinstance(entity, Entity):  # if, not elif!
                    cams.extend(getcams(entity))
            return cams
        return getcams(self)
    
    
    @property
    def transform(self):
        return self._transform
    
    
    @transform.setter
    def transform(self, transform):
        raise RuntimeError('Cannot set transform of SubScene object.')
    
    
    def _update_transform(self, event):
        # Get three components of the transform
        viewbox = self.viewbox_transform
        projection = self.camera.get_projection(event)
        position = self._get_camera_transform()
        # Combine and set
        self._transform = viewbox * projection * position
    
    
    def _get_camera_transform(self):
        """ Calculate the transform from the camera to the SubScene entity.
        This is the inverse of the transform chain *to* the camera.
        """
        
        # Get total transform of the camera
        object = self.camera
        camtransform = object.transform
        
        while True:
            # todo: does it make sense to have a camera in a multi-path?
            object = object.parents[0]
            if object is self:
                break  # Go until we meet ourselves
            if object.transform is not None:
                camtransform = camtransform * object.transform
        
        # Return inverse
        return camtransform.inverse()
    
    
    def paint(self, event):
        
        # todo: update transform only when necessay
        self._update_transform(event)
        
        # Invoke our drawing system
        self.process_system(event, 'draw') 
    
    
    def process_system(self, event, system_name):
        """ Process a system.
        """
        self._systems[system_name].process(event, self)



class ViewBox(Widget):
    """ Provides a rectangular window to which its subscene is rendered
    
    The viewbox defines a certain coordinate frame using a camera (which
    is an entity in the subscene itself). A viewbox also defines
    background color, lights, and has its own drawing system.
    """
    
    def __init__(self, *args, **kwds):
        Widget.__init__(self, *args, **kwds)
        
        # Background color of this viewbox. Used in glClear()
        self._bgcolor = (0.0, 0.0, 0.0, 1.0)
        
        # Init preferred method to provided a pixel grid
        self._preferred_clip_method = 'none'
        
        # Each viewbox has a scene widget, which has a transform that
        # represents the transformation imposed by camera.
        self._scene = SubScene()
        self._scene.parent = self
        
    
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
    
    
    @property
    def camera(self):
        """ The camera associated with this viewbox. Can be None if there
        are no cameras in the scene.
        """
        return self.scene.camera
    
    @camera.setter
    def camera(self, cam):
        """ Get/set the camera of the scene. Equivalent to scene.camera.
        """
        self.scene.camera = cam
    
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if event.press_event is None or not self.rect.contains(*event.press_event.pos[:2]):
            return
            
        self.camera.view_mouse_event(event)

    
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
    
    
    def paint(self, event):
        """ Paint the viewbox. 
        
        This does not really draw *this* object, but prepare for drawing
        our the subscene. In particular, here we calculate the transform
        needed to project the subscene in our viewbox rectangle. Also
        we handle setting a viewport if requested.
        """
        
        # --  Calculate viewbox transformation
        
        # Get the sign of the camera transform of the parent scene. We
        # cannot look at full_transform, since the ViewBox may just be
        # really upside down (intended). The camera transform defines
        # the direction of the dimensions of the coordinate frame.
        # todo: get this sign information in a more effective manner
        # than we can probably also get rid of storing viewbox on event!
        parent_viewbox = event.viewbox
        if parent_viewbox:
            s = parent_viewbox.camera.get_projection(event) * STTransform()
            signx = 1 if s.scale[0] > 0 else -1
            signy = 1 if s.scale[1] > 0 else -1
        else:
            signx, signy = 1, 1
        
        # Determine transformation to make NDC coords (-1..1) map to
        # the viewbox region. The translation is equivalent to doing a
        # (1, 1) shift *after* the scale.
        size = self.size
        trans = STTransform()
        trans.scale = signx * size[0] / 2, signy * size[1] / 2
        trans.translate = size[0] / 2, size[1] / 2
        
        # Set this transform at the scene
        self.scene.viewbox_transform = trans
        
        # -- Calculate resolution
        
        # Get current transform and calculate the 'scale' of the viewbox
        transform = event.full_transform
        p0, p1 = transform.map((0,0)), transform.map(size)
        sx, sy = p1[0] - p0[0], p1[1] - p0[1]

        # From the viewbox scale, we can calculate the resolution. Note that
        # the viewbox scale (sx, sy) applies to the root.
        # todo: we should probably take rotation into account here ...
        canvas_res = event.canvas.size  # root resolution
        w = abs(sx * canvas_res[0] * 0.5)
        h = abs(sy * canvas_res[1] * 0.5)
        
        # Set resolution (note that resolution can be non-integer)
        self._resolution = w, h
        #print(getattr(self, '_name', ''), w, h)
        
        # -- Get user clipping preference
        
        prefer = self.preferred_clip_method
        assert prefer in ('none', 'fragment', 'viewport', 'fbo')
        viewport, fbo = None, None
        
        if prefer == 'none':
            pass
        elif prefer == 'fragment':
            raise NotImplementedError('No fragment shader clipping yet.')
        elif prefer == 'viewport':
            viewport = self._prepare_viewport(event, w, h, signx, signy)
        elif prefer == 'fbo':
            fbo = self._prepare_fbo(event)
        
        # -- Paint
        
        event.push_viewbox(self)
        
        if fbo:
            # Push FBO
            shape = fbo.color_buffer.shape
            rect = 0, 0, shape[1], shape[0]
            transform = event.full_transform * self.scene.viewbox_transform
            event.push_fbo(rect, fbo, transform.inverse())
            #print(self._name, (event.render_transform * self.scene.viewbox_transform).simplify())
            # Clear bg color (handy for dev)
            from vispy.gloo import gl
            clrs = {'':(0.1, 0.1, 0.1), 
                    'vb1':(0.2,0,0), 'vb11':(0.2,0,0.1), 'vb12':(0.2,0,0.2), 
                    'vb2':(0,0.2,0), 'vb21':(0,0.2,0.1), 'vb22':(0,0.2,0.2)}
            clr = clrs[getattr(self,'_name', '')]  # clrs[''] or clrs[getattr(self,'_name', '')]
            gl.glClearColor(clr[0], clr[1], clr[2], 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            # Process childen
            self.scene.paint(event)
            # Pop FBO and now draw the result
            event.pop_fbo()
            self._myprogram.draw(gl.GL_TRIANGLE_STRIP)
            
        elif viewport:
            # Push viewport, draw, pop it
            event.push_viewport(viewport)
            self.scene.paint(event)
            event.pop_viewport()
        
        else:
            # Just draw
            # todo: invoke fragment shader clipping
            self.scene.paint(event)
        
        event.pop_viewbox()
    
    
    def _prepare_viewport(self, event, w, h, signx, signy):
        # Get whether the transform to here is translate-scale only
        rtransform = event.render_transform
        p0 = rtransform.map((0,0))
        px, py = rtransform.map((1,0)), rtransform.map((0,1))
        dx, dy = py[0] - p0[0], px[1] - p0[1]
        
        # Does the transform look scale-trans only?
        if not (dx == 0 and dy == 0):
            return None
            
        # Transform from NDC to viewport coordinates
        canvas_res = event.canvas.size
        tx, ty = py[0], px[1]  # Translation of unit vector
        x = (signx*0.5 + 0.5 + tx) * canvas_res[0] * 0.5
        y = (signy*0.5 + 0.5 + ty) * canvas_res[1] * 0.5
        
        # Round
        return int(x+0.5), int(y+0.5), int(w+0.5), int(h+0.5)
        
    
    def _prepare_fbo(self, event):
        """ Paint the viewbox via an FBO. This method can be applied
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
        
#         # todo: for now we assume scale-translate only!
#         # Get viewport and resolution of parent pixel grid
#         x, y, w, h = self._get_pixel_rect_assuming_st_transform(event)
#         res = event.resolution
        
        # Set texture coords to make the texture be drawn in the right place
        # Note that we would just use -1..1 if we would use a Visual.
        # Note that we need the viewbox transform here!
        coords = (-1, -1, 0), (1, 1, 0)
        transform = event.render_transform * self.scene.viewbox_transform
        coords = [transform.map(c) for c in coords]
        x1, y1, z = coords[0][:3]
        x2, y2, z = coords[1][:3]
        vertexes = np.array([[x1,y1,z], [x2,y1,z], [x1,y2,z], [x2,y2,z]], 
                            np.float32)
        self._vert.set_data(vertexes)
        
        # Set fbo size (mind that this is set using shape!)
        # +1 to create delibirate smoothing
        resolution = [int(i+0.5+1) for i in self._resolution]  # is set in paint()
        shape = resolution[1], resolution[0]
        fbo.color_buffer.resize(shape+(4,))
        fbo.depth_buffer.resize(shape)
        
        return fbo


# todo: What to do with Document. Make dpi a property of the SubScene or ViewBox?
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
    
    def process(self, event, subscene):
        # Iterate over entities
        assert isinstance(subscene, SubScene)
        event.push_entity(subscene)
        for entity in subscene:
            self._process_entity(event, entity)
        event.pop_entity()
    
    def _process_entity(self, event, entity):
        from .visuals import Visual  # todo: import crap
        
        event.canvas._process_entity_count += 1
        
        # Push entity and set its total transform
        event.push_entity(entity)
        
        # If a viewbox, let it render its own subscene 
        if isinstance(entity, ViewBox):
            entity.paint(event)
        # Paint if it is a visual (also if a viewbox)
        elif isinstance(entity, Visual):
#             print(entity, 'in', getattr(event.viewbox, '_name', repr(event.viewbox)))
#             print('  ', event.render_transform.simplify())
#             print('  ', event.path)
            entity.paint(event)
        
        # Processs children; recurse. 
        # Do not go into subscenes (ViewBox.paint processes the subscene)
        if not isinstance(entity, SubScene):
            for sub_entity in entity:
                self._process_entity(event, sub_entity)
        
        event.pop_entity()


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
        trans = transforms.STTransform()
        if True:
            # Origin in top left (flipped y-axis)
            trans.scale = 2.0/w, -2.0/h
            trans.translate = -1, 1
        else:
            # Origin in bottom left
            trans.scale = 2.0/w, 2.0/h
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

