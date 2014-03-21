"""
Demonstrates plugging custom shaders in to a LineVisual.

This allows to modify the appearance of the visual without modifying or
subclassing the original LineVisual class.
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
import vispy.gloo as gloo
from vispy.visuals.line import LineVisual
from vispy.visuals.transforms import Transform, STTransform, arg_to_array
from vispy.shaders.composite import Function
from vispy.visuals import VisualComponent
from vispy.visuals.components import VertexColorComponent

# vertex positions of data to draw
N = 50
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(-0.9, 0.9, N)
pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)

# One array of colors
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

# A custom Transform
class SineTransform(Transform):
    """
    Add sine wave to y-value for wavy effect.
    """
    glsl_map = """
        vec4 $sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y + sin(pos.x), pos.z, 1);
        }"""

    @arg_to_array
    def map(self, coords):
        ret = coords.copy()
        ret[...,1] += np.sin(ret[...,0])
        return ret
    
    @arg_to_array
    def imap(self, coords):
        ret = coords.copy()
        ret[...,1] -= np.sin(ret[...,0])
        return ret

        
        
class DashComponent(VisualComponent):
    """
    VisualComponent that adds dashing to an attached LineVisual.
    """
    
    FRAG_CODE = """
        vec4 $dash(vec4 color) {
            float mod = $distance / $dash_len;
            mod = mod - int(mod);
            color.a = 0.5 * sin(mod*3.141593*2) + 0.5;
            return color;
        }
        """
    
    VERT_CODE = """
        void $dashSup() {
            $output_dist = $distance_attr;
        }
        """
    
    def __init__(self, pos):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self._vbo = None
        self.pos = pos
        
    def _make_vbo(self):
        if self._vbo is None:
            # measure distance along line
            # TODO: this should be recomputed if the line data changes.
            pixel_tr = STTransform(scale=(400,400)) * self.visual.transform
            pixel_pos = pixel_tr.map(self.pos)
            dist = np.empty(pos.shape[0], dtype=np.float32)
            diff = ((pixel_pos[1:] - pixel_pos[:-1]) ** 2).sum(axis=1) ** 0.5
            dist[0] = 0.0
            dist[1:] = np.cumsum(diff)
            self._vbo = gloo.VertexBuffer(dist)
        return self._vbo
        
    def _attach(self, visual):
        super(DashComponent, self)._attach(visual)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        visual._program.add_callback('frag_color', self.frag_func)
        
    def _detach(self):
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        self.visual._program.remove_callback('frag_color', self.frag_func)
        super(DashComponent, self)._detach()
        
    def activate(self, program, mode):
        self.vert_func['distance_attr'] = ('attribute', 
                                                'float', 
                                                self._make_vbo())
        self.vert_func['output_dist'] = ('varying', 'float')
        self.frag_func['dash_len'] = ('uniform', 'float', 20.)
        self.frag_func['distance'] = self.vert_func['output_dist']

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED,)



class Canvas(vispy.app.Canvas):
    def __init__(self):
        
        self.line = LineVisual(pos)
        self.line.transform = (STTransform(scale=(0.1,.3)) * 
                               SineTransform() * 
                               STTransform(scale=(10,3)))
        
        dasher = DashComponent(pos)
        self.line.fragment_components = [VertexColorComponent(color), dasher]
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        
        self.line.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


