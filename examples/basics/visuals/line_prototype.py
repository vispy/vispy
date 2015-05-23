from vispy import app, gloo, visuals
from vispy.visuals.components import Clipper, Alpha, ColorFilter

        

class LineVisual(visuals.Visual):
    """Example of a very simple GL-line visual. 
    
    This shows the minimal set of methods that need to be reimplemented to 
    make a new visual class.
    
    """
    def __init__(self, pos=None, color=(1, 1, 1, 1)):
        vcode = """
        attribute vec2 a_pos;
        
        void main() {
            gl_Position = $transform(vec4(a_pos, 0, 1)); 
            gl_PointSize = 10;
        }
        """
        
        fcode = """
        void main() {
            gl_FragColor = $color;
        }
        """
        
        visuals.Visual.__init__(self, vcode=vcode, fcode=fcode)
        
        self.pos_buf = gloo.VertexBuffer()
        
        # The Visual superclass contains a MultiProgram, which is an object that 
        # behaves like a normal shader program (you can assign shader code, upload
        # values, set template variables, etc.) but internally manages multiple 
        # ModularProgram instances, one per view.
        
        # The MultiProgram is accessed via the `shared_program` property, so
        # the following modifications to the program will be applied to all 
        # views:
        self.shared_program['a_pos'] = self.pos_buf
        self.shared_program.frag['color'] = color
        
        self._need_upload = False
        
        # Visual keeps track of draw mode, index buffer, and GL state. These
        # are shared between all views.
        self._draw_mode = 'line_strip'
        self.set_gl_state('translucent', depth_test=False)
        
        if pos is not None:
            self.set_data(pos)
            
    def set_data(self, pos):
        self._pos = pos
        self._need_upload = True
        
    def _prepare_draw(self, view=None):
        """This method is called immediately before each draw.
        
        The *view* argument indicates which view is about to be drawn.
        """
        if self._need_upload:
            # Note that pos_buf is shared between all views, so we have no need
            # to use the *view* argument in this example. This will be true
            # for most visuals.
            self.pos_buf.set_data(self._pos)
            self._need_upload = False
    
    @staticmethod
    def _prepare_transforms(view):
        """This method is called whenever the TransformSystem instance is
        changed for a view.
        
        Note that each view has its own TransformSystem. In this method we 
        connect the appropriate mapping functions from the view's
        TransformSystem to the view's program.
        """
        
        # Note that we access `view_program` instead of `shared_program`
        # because we do not want this function assigned to other views.
        tr = view.transforms.get_full_transform()
        view.view_program.vert['transform'] = tr
    

class PointVisual(LineVisual):
    """Another simple visual class. 
    
    Due to the simplicity of these example classes, it was only necessary to
    subclass from LineVisual and set the draw mode to 'points'. A more
    fully-featured PointVisual class might not follow this approach.
    """
    def __init__(self, pos=None, color=(1, 1, 1, 1)):
        LineVisual.__init__(self, pos, color)
        self._draw_mode = 'points'
    

class PlotLineVisual(visuals.CompoundVisual):
    """An example compound visual that draws lines and points.
    
    To the user, the compound visual behaves exactly like a normal visual--it
    has a transform system, draw() and bounds() methods, etc. Internally, the
    compound visual automatically manages proxying these transforms and methods
    to its sub-visuals.
    """
    def __init__(self, pos=None, line_color=(1, 1, 1, 1), point_color=(1, 1, 1, 1)):
        self._line = LineVisual(pos, color=line_color)
        self._point = PointVisual(pos, color=point_color)
        visuals.CompoundVisual.__init__(self, [self._line, self._point])


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
    
    # Attach a clipper just to this view. The Clipper filter requires a
    # transform that maps from the framebuffer coordinate system to the 
    # clipping coordinates.
    tr = line.transforms.document_to_framebuffer.inverse
    line.attach(Clipper((20, 20, 260, 260), transform=tr), view=line)
    
    # Make a view of the line that will draw its shadow
    shadow = line.view()
    shadow.transforms.canvas = canvas
    shadow.transform = STTransform(scale=(2, 1), translate=(25, 25))
    shadow.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow)
    tr = shadow.transforms.document_to_framebuffer.inverse
    shadow.attach(Clipper((20, 20, 260, 260), transform=tr), view=shadow)
    
    # And make a second view of the line with different clipping bounds
    view = line.view()
    view.transforms.canvas = canvas
    view.transform = STTransform(scale=(2, 0.5), translate=(450, 150))
    tr = view.transforms.document_to_framebuffer.inverse
    view.attach(Clipper((320, 20, 260, 260), transform=tr), view=view)

    # Make a compound visual
    plot = PlotLineVisual(pos, (0.5, 1, 0.5, 0.2), (0.5, 1, 1, 0.3))
    plot.transforms.canvas = canvas
    plot.transform = STTransform(translate=(80, 450), scale=(1.5, 1))
    tr = plot.transforms.document_to_framebuffer.inverse
    plot.attach(Clipper((20, 320, 260, 260), transform=tr), view=plot)

    # And make a view on the compound 
    view2 = plot.view()
    view2.transforms.canvas = canvas
    view2.transform = STTransform(scale=(1.5, 1), translate=(450, 400))
    tr = view2.transforms.document_to_framebuffer.inverse
    view2.attach(Clipper((320, 320, 260, 260), transform=tr), view=view2)
    
    # And a shadow for the view
    shadow2 = plot.view()
    shadow2.transforms.canvas = canvas
    shadow2.transform = STTransform(scale=(1.5, 1), translate=(455, 405))
    shadow2.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow2)
    tr = shadow2.transforms.document_to_framebuffer.inverse
    shadow2.attach(Clipper((320, 320, 260, 260), transform=tr), view=shadow2)
    

    # Proposed collections API
    #
    # line2 = LineVisual(pos=pos + 20)
    # collection = VisualCollection([line, line2])
    # 
    # def on_draw(event):
    #     collection.draw()  # draws both lines in one pass
    #     

    
    @canvas.connect
    def on_draw(event):
        canvas.context.clear((0.3, 0.3, 0.3, 1.0))
        canvas.context.set_viewport(0, 0, *canvas.physical_size)
        
        shadow.draw()
        line.draw()
        view.draw()
        plot.draw()
        shadow2.draw()
        view2.draw()

    if sys.flags.interactive != 1:
        app.run()
    