
from ..gloo import gl
from . import transforms

class System(object):
    """ A system is an object that does stuff to the Entities in the
    scene. There is one system for each task and systems can be added
    dynamically (also custom ones) to perform specific tasks.
    
    A system typically operates on a specific subset of components of
    the Entities.
    """
    
    def __init__(self):
        pass
    
    
    def process(self, viewbox, root):
        """ Process the given viewbox.
        """
        from .viewbox import ViewBox
        if not isinstance(viewbox, ViewBox):
            raise ValueError('DrawingSystem.draw expects a ViewBox instance.')
        # Init and turn result into a tuple if necessary
        result = self._process_init(viewbox, root)
        if result is None: result = ()
        elif not isinstance(result, tuple): result = (result,)
        # Iterate over entities
        for entity in viewbox:
            self.process_entity(entity, *result)
    
    
    def process_entity(self, entity, *args):
        """ Process the given entity.
        """
        self._root._process_entity_count += 1
        #print('process', entity)
        # Process and turn result into a tuple if necessary
        result = self._process_entity(entity, *args)
        if result is None: result = ()
        elif not isinstance(result, tuple): result = (result,)
        # Iterate over sub entities
        for sub_entity in entity:
            sub_entity._parent = entity  # as promised in the docs of .parent
            self.process_entity(sub_entity, *result)
    
    
    def _process_init(self, viewbox, root):
        """ Called before the system starts processing. Overload this.
        """ 
        return ()
    
    def _process_entity(self, entity, *args):
        """ Called to process an entity. args is what was returned
        from processing the parent. Overload this.
        """
        return ()
 


class DrawingSystem(System):
    """ Simple implementation of a drawing engine.
    """
    
    def _process_init(self, viewbox, root):
        # Store viewbox and root
        self._viewbox, self._root = viewbox, root
        # Camera transform and projection are the same for the
        # entire scene
        self._camtransform = viewbox.camera.get_camera_transform()
        self._projection = viewbox.camera.get_projection(viewbox)
        # Prepare the viewbox (e.g. set up glViewport)
        self._prepare_viewbox(viewbox)
        # Return unit transform
        return transforms.NullTransform()
    
    
    def _process_entity(self, entity, transform):
        #print('processing entity', entity)
        # Set transformation
        if entity.transform is not None:
            transform = transform * entity.transform
        # Draw
        from .visuals import Visual  # todo: import crap
        if isinstance(entity, Visual):
            entity._total_transform = self._projection * self._camtransform * transform
            entity.paint()
        # If a viewbox, render the subscene. 
        from .viewbox import ViewBox  # todo: arg, import order 
        if isinstance(entity, ViewBox):
            entity.process_system(self._root, 'draw')
        # Return new transform
        return transform
    
    
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
