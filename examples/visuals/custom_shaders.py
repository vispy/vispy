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
from vispy.shaders.composite import FragmentFunction, Function

#import pyqtgraph as pg
#c = pg.dbg()
#c.catchNextException()


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
    GLSL_map = Function("""
        vec4 $func_name(vec4 pos) {
            return vec4(pos.x, pos.y + sin(pos.x), pos.z, 1);
        }""")

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


# A custom fragment shader
Dasher = FragmentFunction(
    """
    void $func_name() {
        float mod = $float_distance / $float_dash_len;
        mod = mod - int(mod);
        gl_FragColor.a = 0.5 * sin(mod*3.141593*2) + 0.5;
    }
    """,
    
    vertex_func=Function("""
    void $func_name() {
        $float_output = $float_distance_attr;
    }
    """),
    
    link_vars=[('output', 'distance')],
    vert_hook='vert_post_hook')


class Canvas(vispy.app.Canvas):
    def __init__(self):
        
        self.line = LineVisual(pos, color=color)
        self.line.transform = (STTransform(scale=(0.1,.3)) * 
                               SineTransform() * 
                               STTransform(scale=(10,3)))
        
        pixel_tr = STTransform(scale=(400,400)) * self.line.transform
        pixel_pos = pixel_tr.map(pos)
        dist = np.empty(pos.shape[0], dtype=np.float32)
        diff = ((pixel_pos[1:] - pixel_pos[:-1]) ** 2).sum(axis=1) ** 0.5
        dist[0] = 0.0
        dist[1:] = np.cumsum(diff)
        
        dasher = Dasher.wrap(name="fragment_dasher", 
                             distance_attr=('attribute', 'distance_attr'),
                             dash_len=('uniform', 'dash_len_unif'))
        dasher.fragment_support['distance_attr'] = gloo.VertexBuffer(dist)
        dasher['dash_len_unif'] = 20.
        self.line.add_fragment_callback(dasher)
        
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
    


