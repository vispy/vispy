"""
Basic demonstration of line plotting
"""
import numpy as np
import vispy.app
import vispy.gloo as gloo
from vispy.gloo import gl
from vispy.visuals.line import LineVisual
from vispy.visuals.transforms import STTransform, TransformChain

# vertex positions of rectangle to draw
N = 20
pos = np.zeros((N,3), dtype=np.float32)
pos[:,0] = np.linspace(-0.9, 0.9, N)
pos[:,1] = np.random.normal(size=N, scale=0.2).astype(np.float32)
color = np.ones((N,4), dtype=np.float32)
color[:,0] = np.linspace(0, 1, N)


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.line1 = LineVisual(pos)
        self.line2 = LineVisual(pos)
        self.line2.transform = TransformChain([STTransform(scale=(1, 0.1, 1)), STTransform(translate=(0.1, 0.4, 0))])
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glViewport(0, 0, *self.size)
        self.line1.draw()
        self.line2.draw()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


