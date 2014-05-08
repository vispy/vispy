
from ..gloo import gl
from . import transforms


class System(object):
    """ A system is an object that does stuff to the Entities in the
    scene. There is one system for each task and systems can be added
    dynamically (also custom ones) to perform specific tasks.
    
    A system typically operates on a specific subset of components of
    the Entities.
    There is one system per ViewBox.
    """
    
    def __init__(self):
        pass
    
    
    def process(self, event):
        """ Process the given viewbox.
        """
        viewbox = event.viewbox
        from .viewbox import ViewBox
        if not isinstance(viewbox, ViewBox):
            raise ValueError('DrawingSystem.draw expects a ViewBox instance.')
        # Init and turn result into a tuple if necessary
        result = self._process_init(event)
        if result is None: result = ()
        elif not isinstance(result, tuple): result = (result,)
        # Iterate over entities
        for entity in viewbox:
            self.process_entity(event, entity)
    
    
    def process_entity(self, event, entity):
        """ Process the given entity.
        """
        self._root._process_entity_count += 1
        #print('process', entity)
        # Process and turn result into a tuple if necessary
        result = self._process_entity(event, entity)
        if result is None: result = ()
        elif not isinstance(result, tuple): result = (result,)
        # Iterate over sub entities
        for sub_entity in entity:
            sub_entity._parent = entity  # as promised in the docs of .parent
            self.process_entity(event, sub_entity)
    
    
    def _process_init(self, event):
        """ Called before the system starts processing. Overload this.
        """ 
        return ()
    
    def _process_entity(self, event, entity):
        """ Called to process an entity. args is what was returned
        from processing the parent. Overload this.
        """
        return ()
 


class DrawingSystem(System):
    """ Simple implementation of a drawing engine.
    
    There is one system per viewbox. When we encounter a viewbox, one
    of three things can/should happen:
      * we use glViewPort to create a new viewport with clipping. The
        chain of transformations is thus reset from this point.
      * we use an FBO to draw the subscene in the viewbox. The chain
        of transformations is thus reset from this point. This should
        also happen when we need the viewbox to have a specific
        resolution.
      * we do use neither (but apply clipping in fragment shader). Now
        the complete chain of transforms (from the last viewport) must
        be taken into account.
    
    """
    
    
    def process(self, event):
        from .viewbox import ViewBox
        
        viewbox = event.viewbox
        root = event.canvas
        if not isinstance(viewbox, ViewBox):
            raise ValueError('DrawingSystem.draw expects a ViewBox instance.')
        
        # Get camera transforms
        camtransform = self._get_camera_transform(viewbox.camera)
        projection = viewbox.camera.get_projection(viewbox)
        
        # Iterate over entities
        for entity in viewbox:
            self._process_entity(event, entity)
    
    def _process_entity(self, event, entity):
        self._root._process_entity_count += 1
        
        event.push_entity(entity)
        
        # Draw
        #print(event.path)
        from .visuals import Visual  # todo: import crap
        if isinstance(entity, Visual):
            entity._total_transform = self._projection * self._camtransform * \
                                      event.viewport_transform
            entity.paint()
        # If a viewbox, render the subscene. 
        from .viewbox import ViewBox  # todo: arg, import order
        
        if isinstance(entity, ViewBox):
            # todo: check that all transforms in event.path are translate+scale 
            # todo: check that camera is is pixel or NDC
            viewport = ////
            event.push_viewbox(entity, viewport)
            #transform = self._projection * self._camtransform * event.viewport_transform
            entity.process_system(event, 'draw')
            event.pop_viewbox(entity, viewport)
        else:
            for sub_entity in entity:
                self._process_entity(event, sub_entity)
        
        event.pop_entity()
    
    
    def _process_init(self, event):
        # Store viewbox and root
        viewbox = event.total_path[-1] 
        self._viewbox, self._root = viewbox, event.canvas
        # Camera transform and projection are the same for the entire sub-scene
        self._camtransform = self._get_camera_transform(viewbox.camera)
        self._projection = viewbox.camera.get_projection(viewbox)
        
        # Prepare the viewbox (e.g. set up glViewport)
        
        # only. If not, we cannot use a viewport here!
        #self._prepare_viewbox(viewbox)
        # Return unit transform
        return transforms.NullTransform()
    
    
    def _process_entity(self, event, entity):
        #print('processing entity', entity)
        event.push_entity(entity)
        # Draw
        #print(event.path)
        from .visuals import Visual  # todo: import crap
        if isinstance(entity, Visual):
            entity._total_transform = self._projection * self._camtransform * \
                                      event.viewport_transform
            entity.paint()
        # If a viewbox, render the subscene. 
        from .viewbox import ViewBox  # todo: arg, import order
        if isinstance(entity, ViewBox):
            # todo: check that all transforms in event.path are translate+scale 
            # todo: check that camera is is pixel or NDC
            viewport = ////
            event.push_viewbox(entity, viewport)
            #transform = self._projection * self._camtransform * event.viewport_transform
            entity.process_system(event, 'draw')
            event.pop_viewbox(entity, viewport)
        
        # Return new transform
        #return transform
    
    
    def _prepare_viewbox(self, viewbox):
        # print('preparing viewbox', viewbox )
        M = viewbox.transform
        w, h = int(2.0/M.scale[0]), int(2.0/M.scale[1])
        x, y = int(2.0/M.translate[0]), int(2.0/M.translate[1])
        
        need_FBO = False
#         need_FBO |= bool( M[0,1] or M[0,2] or M[1,0] or M[1,2] or M[2,0] or M[2,1] )
#         need_FBO |= (w,h) != viewbox.resolution
        
        # todo: take parent viewboxes into account.
        
        if need_FBO:
            # todo: we cannot use a viewbox or scissors, but need an FBO
            raise NotImplementedError('Need FBO to draw this viewbox')
        else:
            # nice rectangle, we can use viewbox and scissors
            gl.glViewport(x, y, w, h)
            gl.glScissor(x, y, w, h)
            gl.glEnable(gl.GL_SCISSOR_TEST)
            # Draw bgcolor
            gl.glClearColor(*viewbox.bgcolor)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    
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
