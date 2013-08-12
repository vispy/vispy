from vispy.oogl import ShaderProgram, VertexShader, FragmentShader, VertexBuffer
import OpenGL.GL as gl
import vispy.shaders.transforms as transforms
from vispy.util.six import string_types
import numpy as np
    

"""
Names assigned to commonly-used combinations of GL flags
"""
GLOptions = {
    'opaque': {
        gl.GL_DEPTH_TEST: True,
        gl.GL_BLEND: False,
        gl.GL_ALPHA_TEST: False,
        gl.GL_CULL_FACE: False,
    },
    'translucent': {
        gl.GL_DEPTH_TEST: True,
        gl.GL_BLEND: True,
        gl.GL_ALPHA_TEST: False,
        gl.GL_CULL_FACE: False,
        'glBlendFunc': (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA),
    },
    'additive': {
        gl.GL_DEPTH_TEST: False,
        gl.GL_BLEND: True,
        gl.GL_ALPHA_TEST: False,
        gl.GL_CULL_FACE: False,
        'glBlendFunc': (gl.GL_SRC_ALPHA, gl.GL_ONE),
    },
}


class Visual(object):
    """
    Base class for low-level visuals. 
    
    Provides:
    
    * Methods for establishing GL state before drawing
      (ie, glEnable/Disable and related calls)
    * Methods for determining coordinate transformations to be applied to vertex data
    
    """
    def __init__(self):
        self.__transforms = []
        self.__gl_opts = {}
        
    @property
    def transforms(self):
        return self.__transforms[:]
    
    @transforms.setter
    def transforms(self, tr):
        assert isinstance(tr, list)
        self.__transforms = tr
        self.update()
        
    def transform_chain(self):
        return transforms.TransformChain(self.transforms, function='global_transform')
        
    def draw(self):
        """ Draw this item.
        """
        # do glEnable/Disable and related calls
        self.setup_gl_state() 
        
        # draw here..
    
    def init_gl(self):
        pass
    
    @classmethod
    def draw_multi(self, visuals):
        """
        Draw multiple visuals in a single pass.
        
        Requires items in *visuals* to be compatible.
        Subclasses are not required to reimplement this method.
        """
        pass

    def set_gl_options(self, opts):
        """
        Set the OpenGL state options to use immediately before drawing this item.
        (Note that subclasses must call setup_gl_state before painting for this to work)
        
        The simplest way to invoke this method is to pass in the name of
        a predefined set of options (see the GLOptions variable):
        
        ============= ======================================================
        opaque        Enables depth testing and disables blending
        translucent   Enables depth testing and blending
                      Elements must be drawn sorted back-to-front for
                      translucency to work correctly.
        additive      Disables depth testing, enables blending.
                      Colors are added together, so sorting is not required.
        ============= ======================================================
        
        It is also possible to specify any arbitrary settings as a dictionary. 
        This may consist of {'functionName': (args...)} pairs where functionName must 
        be a callable attribute of OpenGL.GL, or {GL_STATE_VAR: bool} pairs 
        which will be interpreted as calls to glEnable or glDisable(GL_STATE_VAR).
        
        For example::
            
            {
                GL_ALPHA_TEST: True,
                GL_CULL_FACE: False,
                'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
            }
            
        
        """
        if isinstance(opts, string_types):
            opts = GLOptions[opts]
        self.__gl_opts = opts.copy()
        self.update()
        
    def update(self):
        """ Called when the Visual needs to be redrawn
        """
        
    def update_gl_options(self, opts):
        """
        Modify the OpenGL state options to use immediately before drawing this item.
        *opts* must be a dictionary as specified by setGLOptions.
        Values may also be None, in which case the key will be ignored.
        """
        self.__gl_opts.update(opts)
        
    def setup_gl_state(self):
        """
        This method is responsible for preparing the GL state options needed to render 
        this item (blending, depth testing, etc). The method is called immediately before painting the item.
        """
        for k,v in self.__gl_opts.items():
            if v is None:
                continue
            if isinstance(k, string_types):
                func = getattr(gl, k)
                func(*v)
            else:
                if v is True:
                    gl.glEnable(k)
                else:
                    gl.glDisable(k)


