try:
    import cv2
except:
    print("You need OpenCV for this example.")
    cv2 = None
    
import numpy as np
from vispy import app
from vispy import gloo

vertex = """
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_texcoord = texcoord;
    }
"""

fragment = """
    uniform sampler2D texture;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(texture, v_texcoord);
        
        // HACK: the image is in BGR instead of RGB.
        float temp = gl_FragColor.r;
        gl_FragColor.r = gl_FragColor.b;
        gl_FragColor.b = temp;
    }
"""

kernel = np.array([[1, 0, -1], [2, 0, -1], [1, 0, -1]], dtype=np.float32)
kernel /= kernel.sum()


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(640, 480), close_keys='escape')
        self.program = gloo.Program(vertex, fragment, count=4)
        self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.program['texcoord'] = [(1, 1), (1, 0), (0, 1), (0, 0)]
        self.program['texture'] = np.zeros((480, 640, 3)).astype(np.uint8)
        if cv2 is not None:
            self.cap = cv2.VideoCapture(0)
        self._timer = app.Timer(1 / 100.)
        self._timer.connect(self.on_timer)
        self._timer.start()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear((0, 0, 0, 0))
        if cv2 is not None:
            _, im = self.cap.read()
        else:
            im = np.random.randint(size=(480, 640, 3), 
                                   low=0, high=255).astype(np.uint8)
        self.program['texture'][...] = im
        self.program.draw('triangle_strip')
        
    def on_timer(self, event):
        self.update()
        
c = Canvas()
c.show()
app.run()
if cv2 is not None:
    c.cap.release()
