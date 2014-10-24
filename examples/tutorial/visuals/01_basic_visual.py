"""
Very simple demonstration of a basic visual: a rectangle with a specialized 
fragment shader.

"""
from vispy import app, gloo, visuals
import numpy as np


vertex_shader = """
void main() {
   gl_Position = $transform(vec4($position, 0, 1));
}
"""

fragment_shader = """
void main() {
  gl_FragColor = $color;
}
"""


class MyRect(visuals.Visual):
    def __init__(self, x, y, w, h):
        visuals.Visual.__init__(self)
        # vertices for two triangles forming a rectangle
        self.vbo = gloo.VertexBuffer(np.array([
            [x, y], [x+w, y], [x+w, y+h],
            [x, y], [x+w, y+h], [x, y+h]
            ], dtype=np.float32))
        self.program = visuals.shaders.ModularProgram(vertex_shader, 
                                                      fragment_shader)
        self.program.vert['position'] = self.vbo
        self.program.frag['color'] = (1, 0, 0, 1)
        
    def draw(self, transforms):
        self.program.vert['transform'] = transforms.get_full_transform()
        self.program.draw('triangles')
        


if __name__ == '__main__':
    rect = MyRect(100, 100, 200, 300)
    canvas = app.Canvas(keys='interactive', show=True)
    tr_sys = visuals.transforms.TransformSystem(canvas)
    @canvas.events.draw.connect
    def draw(event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *canvas.size)
        rect.draw(tr_sys)
    
    import sys
    if sys.flags.interactive == 0:
        app.run()