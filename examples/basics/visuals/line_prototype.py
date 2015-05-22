from vispy import app, gloo, visuals
from vispy.visuals.components import Clipper, Alpha, ColorFilter

        

class LineVisual(visuals.Visual):
    def __init__(self, pos=None):
        vcode = """
        attribute vec2 a_pos;
        
        void main() {
            gl_Position = $transform(vec4(a_pos, 0, 1)); 
        }
        """
        
        fcode = """
        void main() {
            gl_FragColor = $color;
        }
        """
        
        visuals.Visual.__init__(self, vcode=vcode, fcode=fcode)
        
        self.pos_buf = gloo.VertexBuffer()
        self.shared_program['a_pos'] = self.pos_buf
        self.shared_program.frag['color'] = (1, 1, 0.5, 1)
        self._need_upload = False
        
        self._draw_mode = 'line_strip'
        
        if pos is not None:
            self.set_data(pos)
            
    def set_data(self, pos):
        self._pos = pos
        self._need_upload = True
        
    def _prepare_draw(self, view=None):
        if self._need_upload:
            self.pos_buf.set_data(self._pos)
            self._need_upload = False
    
    @staticmethod
    def _prepare_transforms(view):
        view.view_program.vert['transform'] = view.transforms.get_full_transform()
    

if __name__ == '__main__':
    import sys
    import numpy as np
    from vispy.visuals.transforms import STTransform
    
    canvas = app.Canvas(keys='interactive', size=(600, 600), show=True)
    pos = np.random.normal(size=(100,2), loc=300, scale=50).astype('float32')
    line = LineVisual(pos=pos)
    line.transforms.canvas = canvas
    line.attach(ColorFilter((0.5, 1, 1, 1)))
    
    v1 = line.view()
    v1.transforms.canvas = canvas
    v1.transform = STTransform(scale=(0.5, 2), translate=(100, 100))
    #v1.attach(Clipper(...), all_views=False)
    
    v2 = line.view()
    v2.transforms.canvas = canvas
    v2.transform = STTransform(scale=(2, 0.5), translate=(-100, -100))
    #v2.attach(ColorFilter((1, 1, 1, 0.5)), all_views=False)
    
    @canvas.connect
    def on_draw(event):
        canvas.context.set_viewport(0, 0, *canvas.physical_size)
        line.draw()
        v1.draw()
        v2.draw()
        

    if sys.flags.interactive != 1:
        app.run()
    