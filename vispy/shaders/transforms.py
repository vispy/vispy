from vispy.oogl import ShaderProgram, VertexShader, FragmentShader, VertexBuffer
#from OpenGL.GL import *
import OpenGL.GL as gl
import numpy as np

## todo: make transforms their own top-level module?

class Transform(VertexShader):
    """ Generic template class for vertex transformation shaders
    
    All Transform classes perform a different type of transformation,
    and include both GLSL and python code for performing the forward
    and reverse mappings.
    
    In general, transformations should only ever be done using the
    map() and imap() methods. In some cases, imap() may return None.
    """
    def __init__(self, source=None):
        super(Transform, self).__init__(source)
    
    def map(self, coords):
        pass
    
    def imap(self, coords):
        pass
    
    def __mul__(self, tr):
        #return TransformChain([self, tr])
        return NotImplemented
        
        

class TransformChain(Transform):
    """ Transform shader built from a series of Transform shaders.
    
    Will collapse adjacent transforms if possible.
    """
    def __init__(self, transforms = None):
        if transforms is None:
            transforms = []
        self._transforms = transforms
    
    def append(self, tr):
        self._transforms.append(tr)
        
    def prepend(self, tr):
        self._transforms.insert(0, tr)

class NullTransform(Transform):
    """ Transform having no effect on coordinates.
    """
    def __init__(self):
        super(NullTransform, self).__init__()
        self.set_source("""
            #version 120

            vec4 global_transform(vec4 pos) {
                return pos;
            }
            """)
            



class STTransform(Transform):
    """ Transform perfoming only scale and translate
    """
    def __init__(self, scale=None, translate=None):
        Transform.__init__(self, """
            #version 120

            uniform vec3 STTransform_translate;
            uniform vec3 STTransform_scale;

            vec4 global_transform(vec4 pos) {
                return (pos * vec4(STTransform_scale, 1)) + vec4(STTransform_translate, 0);
            }
            """)
            
        self._scale = np.ones(3, dtype=np.float32)
        self._translate = np.zeros(3, dtype=np.float32)
        
        self.scale = (1.0, 1.0, 1.0) if scale is None else scale
        self.translate = (0.0, 0.0, 0.0) if translate is None else translate
        
            
    def map(self, coords):
        n = coords.shape[-1]
        return coords * self.scale[:n] + self.translate[:n]
    
    def imap(self, coords):
        n = coords.shape[-1]
        return (coords - self.translate[:n]) / self.scale[:n]
            
    @property
    def scale(self):
        return self._scale.copy()
    
    @scale.setter
    def scale(self, s):
        self._scale[:len(s)] = s
        self._scale[len(s):] = 1.0
        self._update()
        
    @property
    def translate(self):
        return self._translate.copy()
    
    @translate.setter
    def translate(self, t):
        self._translate[:len(t)] = t
        self._translate[len(t):] = 0.0
        self._update()
        
    def _on_enabling(self, program):
        super(STTransform, self)._on_enabling(program)
        self._update()
        
    def _update(self):
        # Send uniforms to currently-enabled program, if any.
        if self._program is not None:            
            self._program.uniforms['STTransform_scale'] = self.scale
            self._program.uniforms['STTransform_translate'] = self.translate
    
    def as_affine(self):
        m = AffineTransform()
        m.scale(self.scale)
        m.translate(self.translate)
        return m
    
    def __mul__(self, tr):
        if isinstance(tr, STTransform):
            s = self.scale * tr.scale
            t = self.translate + (tr.translate * self.scale)
            return STTransform(scale=s, translate=t)
        elif isinstance(tr, AffineTransform):
            return self.as_affine() * tr
        else:
            return NotImplemented
            
    def __repr__(self):
        return "<STTransform scale=%s translate=%s>" % (self.scale, self.translate)

class AffineTransform(Transform):
    def __init__(self):
        self.matrix = np.eye(4)
        self.inverse = None
        Transform.__init__(self, """
            #version 120

            uniform mat4 transform;

            vec4 global_transform(vec4 pos) {
                return transform * pos;
            }
            """)
    
    def map(self, coords):
        return np.dot(self.matrix, coords)
    
    def imap(self, coords):
        if self.inverse is None:
            self.inverse = np.linalg.invert(self.matrix)
        return np.dot(self.inverse, coords)


class SRTTransform(Transform):
    """ Transform performing scale, rotate, and translate
    """
    
class ProjectionTransform(Transform):
    @classmethod
    def frustum(cls, l, r, t, b, n, f):
        pass

class LogTransform(Transform):
    pass

class PolarTransform(Transform):
    pass

class BilinearTransform(Transform):
    pass

class WarpTransform(Transform):
    """ Multiple bilinear transforms in a grid arrangement.
    """
