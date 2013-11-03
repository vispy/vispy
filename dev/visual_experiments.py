from vispy import gloo
from vispy import app
from vispy.gloo import gl
from disc_collection import DiscCollection
import numpy as np


class Canvas(app.Canvas):
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        n = 10000
        self.discs = DiscCollection()
        self.discs.line_width = 2.
        self.discs.position = 0.25 * np.random.randn(n, 2).astype(np.float32)
        self.discs.color = np.random.uniform(0,1,(n,3)).astype(np.float32)
        self.discs.size = np.random.uniform(2,12,(n,1)).astype(np.float32)
        
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
    
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        self.discs.draw()
        
if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
