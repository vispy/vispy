from __future__ import division

from vispy import app, scene, visuals, gloo
from vispy.util import filter, ptime
import numpy as np


class VectorFieldVisual(visuals.Visual):
    vertex = """
    uniform sampler2D field;
    attribute vec2 index;
    uniform vec2 shape;
    uniform vec2 field_shape;
    uniform float spacing;
    varying float dist;
    varying vec2 ij;
    uniform sampler2D offset;
    varying float flow_rate;
    uniform float seg_len;
    
    void main() {
        // distance along one line
        dist = index.y * seg_len;
        
        vec2 local;
        ij = vec2(mod(index.x, shape.x), floor(index.x / shape.y));
        // *off* is a random offset to the starting location, which prevents
        // the appearance of combs in the field 
        vec2 off = texture2D(offset, ij / shape).xy - 0.5;
        local = spacing * (ij + off);
        for( int i=0; i<index.y; i+=1 ) {
            vec2 uv = local / field_shape;
            vec2 dir = texture2D(field, uv).xy;
            flow_rate = log(length(dir));
            local += seg_len * normalize(dir);
        }
        gl_Position = $transform(vec4(local, 0, 1));
    }
    """
    
    fragment = """
    uniform float time;
    uniform float speed;
    varying float dist;
    varying vec2 ij;
    uniform sampler2D offset;
    uniform sampler2D color;
    uniform vec2 shape;
    varying float flow_rate;
    uniform float nseg;
    uniform float seg_len;
    
    void main() {
        float totlen = nseg * seg_len;
        float phase = texture2D(offset, ij / shape).b;
        float alpha;
        alpha = mod((dist / totlen) + phase - time, 1);
        alpha *= (1 - cos(2 * 3.141592 * dist / totlen)) * 0.5;
        vec4 base_color = texture2D(color, ij / shape);
        gl_FragColor = vec4(base_color.rgb, base_color.a * alpha);
    }
    """
    
    def __init__(self, field, spacing=10, segments=3, seg_len=0.5):
        self._time = 0.0
        self._last_time = ptime.time()
        rows = field.shape[0] / spacing
        cols = field.shape[1] / spacing
        index = np.empty((rows * cols, segments * 2, 2), dtype=np.float32)
        
        # encodes starting position within vector field
        index[:, :, 0] = np.arange(rows * cols)[:, np.newaxis]
        # encodes distance along length of line
        index[:, ::2, 1] = np.arange(segments)[np.newaxis, :]
        index[:, 1::2, 1] = np.arange(segments)[np.newaxis, :] + 1
        self._index = gloo.VertexBuffer(index)
        color = np.array([[[1, 1, 1, 0.3]]], dtype='float32')
        self._color = gloo.Texture2D(color)
        
        offset = np.random.uniform(256, size=(rows, cols, 3)).astype(np.ubyte)
        self._offset = gloo.Texture2D(offset, format='rgb')
        self._field = gloo.Texture2D(field, format='rg', internalformat='rg32f',
                                     interpolation='linear')
        self._field_shape = field.shape[:2]
        
        visuals.Visual.__init__(self, vcode=self.vertex, fcode=self.fragment)
        
        self.shared_program['field'] = self._field
        self.shared_program['field_shape'] = self._field.shape[:2]
        self.shared_program['shape'] = (rows, cols)
        self.shared_program['index'] = self._index
        self.shared_program['spacing'] = spacing
        self.shared_program['t'] = self._time
        self.shared_program['offset'] = self._offset
        self.shared_program['speed'] = 10
        self.shared_program['color'] = self._color
        self.shared_program['seg_len'] = seg_len
        self.shared_program['nseg'] = segments
        
        self._draw_mode = 'lines'
        self.set_gl_state('translucent', depth_test=False)
        
        self.timer = app.Timer(interval='auto', connect=self.update_time)
        self.timer.start()
        
    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()
        
    def _prepare_draw(self, view):
        pass
    
    def _compute_bounds(self, axis, view):
        if axis > 1:
            return (0, 0)
        return (0, self._field_shape[axis])

    def update_time(self, ev):
        t = ptime.time()
        self._time += t - self._last_time
        self._last_time = t
        self.shared_program['time'] = self._time
        self.update()


VectorField = scene.visuals.create_visual_node(VectorFieldVisual)



field = np.zeros((100, 100, 3), dtype='float32')
field[..., 0] = np.fromfunction(lambda x,y: x-50, (100, 100))
field[..., 1] = np.fromfunction(lambda x,y: y-50, (100, 100))

win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view(camera='panzoom')
#img = scene.Image(field, parent=view.scene)

vfield = VectorField(field[..., :2], spacing=0.5, segments=30, seg_len=0.5, parent=view.scene)
view.camera.set_range()




if __name__ == '__main__':
    app.run()
