from vispy import app, scene, visuals, gloo, plot
from vispy.scene.visuals import create_visual_node
from vispy.util import filter 
import numpy as np


class ScrollingLinesVisual(visuals.Visual):
    vertex_code = """
    uniform sampler2D position;
    uniform vec2 pos_size;
    attribute vec2 index;  // .x=line #, .y=vertex #
    
    void main() {
        vec4 pos = vec4(texture2D(position, index * (pos_size-1)).xyz, 1);
        gl_Position = $transform(pos);
    }
    """
    
    fragment_code = """
    void main() {
        gl_FragColor = vec4(0, 0, 0, 1);
    }
    """
    
    def __init__(self):
        """Displays many lines of equal length, with the option to add new
        vertex data to one end of the lines.
        """
        self._pos_tex = gloo.Texture2D(shape=(10, 10, 3), format='rgb', internalformat='rgb32f')
        self._index_buf = gloo.VertexBuffer()
        
        visuals.Visual.__init__(self, vcode=self.vertex_code, fcode=self.fragment_code)
        
        self.shared_program['position'] = self._pos_tex
        self.shared_program['index'] = self._index_buf
        self._draw_mode = 'line_strip'
        
    def set_data(self, data):
        data = data.astype('float32')
        self._pos_tex.set_data(data)
        self.shared_program['pos_size'] = data.shape[:2][::-1]
        index = np.empty((data.shape[0], data.shape[1], 2), dtype='float32')
        index[..., 1] = np.arange(data.shape[0])[:, np.newaxis]
        index[..., 0] = np.arange(data.shape[1])[np.newaxis, :]
        self._index_buf.set_data(index)

    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()
        
    def _prepare_draw(self, view):
        pass
    
    def _compute_bounds(self, axis, view):
        return self._pos_tex[..., axis].min(), self.pos_tex[..., axis].max()


ScrollingLines = create_visual_node(ScrollingLinesVisual)

win = plot.Fig()
plt = win[0, 0]

N = 2
M = 20

lines = ScrollingLines(parent=plt.view.scene)

data = np.empty((N, M, 3))
#data[:, :M] = np.random.normal(size=(N, M), scale=30)
#data[:, :M] = filter.gaussian_filter(data[:, :M], (1, 100))
#data[:, :M] += np.random.normal(size=(N, M), scale=6)
#data[:, :M] = filter.gaussian_filter(data[:, :M], (0, 10))
#data[:, :M] += np.random.normal(size=(N, M), scale=0.6)
#data[:, M:] = data[:, :M]
data[..., 0] = np.linspace(0, 1, M)[np.newaxis, :]
data[..., 1] = np.random.normal(size=(N, M), scale=0.1)
lines.set_data(data)

#ptr = 0
#def update(ev):
    #global ptr
    #d = np.empty((M, 2))
    #d[:, 0] = np.linspace(0, 10, M)
    #for i, l in enumerate(lines):
        #d[:, 1] = data[i, ptr:ptr+M]
        #l.set_data(d.copy())
    #ptr = (ptr + 100) % M

#timer = app.Timer(connect=update, interval=0.03)
#timer.start()


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
