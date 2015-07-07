from __future__ import division

from vispy import app, scene, visuals, gloo
from vispy.util import filter 
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
    
    void main() {
        dist = index.y * spacing;
        vec2 local;
        ij = vec2(mod(index.x, shape.x), floor(index.x / shape.y));
        local.x = spacing * ij.x;
        local.y = spacing * ij.y;
        for( int i=0; i<index.y; i+=1 ) {
            vec2 uv = local / field_shape;
            vec2 dir = texture2D(field, uv).xy;
            local += spacing * normalize(dir);
        }
        gl_Position = $transform(vec4(local, 0, 1));
    }    
    """
    
    fragment = """
    uniform float phase;
    varying float dist;
    varying vec2 ij;
    uniform sampler2D phase_offset;
    uniform vec2 shape;
    
    void main() {
        float offset = texture2D(phase_offset, ij / shape).r * 2 * 3.1415;
        float alpha = (sin(dist*3 - phase + offset) + 1) * 0.5;
        gl_FragColor = vec4(1, 1, 1, alpha);
    }    
    """
    
    def __init__(self, field, spacing=10):
        self._phase = 0.0
        rows = field.shape[0] / spacing
        cols = field.shape[1] / spacing
        index = np.empty((rows * cols * 2, 2), dtype=np.float32)
        index[0::2, 0] = np.arange(rows * cols)
        index[1::2, 0] = index[::2, 0]
        index[0::2, 1] = 0
        index[1::2, 1] = 1
        self._index = gloo.VertexBuffer(index)
        offset = np.random.uniform(256, size=(rows, cols)).astype(np.ubyte)
        print offset
        self._phase_offset = gloo.Texture2D(offset, format='luminance')
        self._field = gloo.Texture2D(field, format='rg', internalformat='rg32f',
                                     interpolation='linear')
        self._field_shape = field.shape[:2]
        
        visuals.Visual.__init__(self, vcode=self.vertex, fcode=self.fragment)
        
        self.shared_program['field'] = self._field
        self.shared_program['field_shape'] = self._field.shape[:2]
        self.shared_program['shape'] = (rows, cols)
        self.shared_program['index'] = self._index
        self.shared_program['spacing'] = spacing
        self.shared_program['phase'] = self._phase
        self.shared_program['phase_offset'] = self._phase_offset
        
        self._draw_mode = 'lines'
        self.set_gl_state('translucent')
        
        self.timer = app.Timer(interval='auto', connect=self.update_phase)
        self.timer.start()
        
    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()
        
    def _prepare_draw(self, view):
        pass
    
    def _compute_bounds(self, axis, view):
        if axis > 1:
            return (0, 0)
        return (0, self._field_shape[axis])

    def update_phase(self, ev):
        self._phase += 0.07
        self.shared_program['phase'] = self._phase
        self.update()


VectorField = scene.visuals.create_visual_node(VectorFieldVisual)



field = np.zeros((100, 100, 3), dtype='float32')
field[..., 0] = np.fromfunction(lambda x,y: y-50, (100, 100))
field[..., 1] = np.fromfunction(lambda x,y: x-50, (100, 100))

win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view(camera='panzoom')
#img = scene.Image(field, parent=view.scene)

vfield = VectorField(field[..., :2], spacing=2, parent=view.scene)
view.camera.set_range()




if __name__ == '__main__':
    app.run()
