"""
Basic demonstration of line plotting
"""
import numpy as np
import vispy.app
import vispy.gloo as gloo
from vispy.gloo import gl
from vispy.visuals.line import LineVisual
from vispy.visuals.transforms import STTransform, TransformChain, LogTransform, AffineTransform

# vertex positions of rectangle to draw
N = 100
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(-0.9, 0.9, N)
pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(vispy.app.Canvas):
    def __init__(self):
        colors = [color, (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
                  (1, 1, 0, 1), (0, 1, 1, 1), (1, 0, 1, 1)]
        self.lines = [LineVisual(pos, color=colors[i]) for i in range(5)]
        self.lines[1].transform = STTransform(scale=(1, 0.1, 1))
        self.lines[2].transform = TransformChain([
                                    STTransform(scale=(1, 0.1, 1)), 
                                    STTransform(translate=(0.1, 0.5, 0))])
        self.lines[3].transform = TransformChain([
                                    STTransform(translate=(1.1, -0.7, 0)), 
                                    LogTransform(base=(10, 0, 0))])
        self.lines[4].transform = AffineTransform()
        self.lines[4].transform.translate((0.5, -0.5, 0))
        self.lines[4].transform.scale((0.1, 0.1, 1))
        self.lines[4].transform.rotate(45, (0, 0, 1))
        
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glViewport(0, 0, *self.size)
        for line in self.lines:
            line.draw()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


