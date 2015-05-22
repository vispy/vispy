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
        self.shared_program.frag['color'] = (1, 1, 1, 1)
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
    pos = np.random.normal(size=(1000,2), loc=0, scale=50).astype('float32')
    pos[0] = [0, 0]
    
    # Make a line visual
    line = LineVisual(pos=pos)
    line.transforms.canvas = canvas
    line.transform = STTransform(scale=(2, 1), translate=(20, 20))
    
    # Attach color filter to all views (current and future) of the visual
    line.attach(ColorFilter((1, 1, 0.5, 0.7)))
    
    # Attach a clipper just to this view
    tr = line.transforms.document_to_framebuffer.inverse
    line.attach(Clipper((20, 20, 260, 260), transform=tr), view=line)
    
    # Make a view of the line that will draw its shadow
    shadow = line.view()
    shadow.transforms.canvas = canvas
    shadow.transform = STTransform(scale=(2, 1), translate=(25, 25))
    shadow.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow)
    shadow.set_gl_state('translucent', depth_test=False)
    tr = shadow.transforms.document_to_framebuffer.inverse
    shadow.attach(Clipper((20, 20, 260, 260), transform=tr), view=shadow)
    
    # And make a second view of the line with different clipping bounds
    view = line.view()
    view.transforms.canvas = canvas
    view.transform = STTransform(scale=(2, 0.5), translate=(450, 150))
    tr = view.transforms.document_to_framebuffer.inverse
    view.attach(Clipper((320, 20, 260, 260), transform=tr), view=view)


    
    @canvas.connect
    def on_draw(event):
        canvas.context.clear((0.3, 0.3, 0.3, 1.0))
        canvas.context.set_viewport(0, 0, *canvas.physical_size)
        
        shadow.draw()
        line.draw()
        view.draw()
        

    if sys.flags.interactive != 1:
        app.run()
    