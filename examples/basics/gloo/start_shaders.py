from vispy import gloo
from vispy import app
import numpy as np

VERT_SHADER = """
#version 120
attribute vec2 a_position;
void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    gl_PointSize = 10.0;
}
"""

FRAG_SHADER = """
#version 120
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = np.random.uniform(-0.5, 0.5, size=(20, 2))

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear('white')
        self.program.draw('points')

c = Canvas()
c.show()
app.run()
