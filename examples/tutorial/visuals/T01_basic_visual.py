"""
Tutorial: Creating Visuals
--------------------------

This tutorial is intended to guide developers who are interested in creating 
new subclasses of Visual. In most cases, this will not be necessary because
vispy's base library of visuals will be sufficient to create complex scenes as
needed. However, there are cases where a particular visual effect is desired 
that is not supported in the base library, or when a custom visual is needed to
optimize performance for a specific use case.

The purpose of a Visual is to encapsulate a single drawable object. This
drawable can be as simple or complex as desired. Some of the simplest visuals 
draw points, lines, or triangles, whereas more complex visuals invove multiple
drawing stages or make use of sub-visuals to construct larger objects.

In this example we will create a very simple Visual that draws a rectangle.
Visuals are defined by:

1. Creating a subclass of vispy.visuals.Visual
2. Defining a draw() method that takes into account some user-specified
   transformation functions.


"""
from vispy import app, gloo, visuals, scene
import numpy as np

# Define a simple vertex shader. We use $template variables as placeholders for
# code that will be inserted later on. In this example, $position will become
# an attribute, and $transform will become a function. Important: using
# $transform in this way ensures that users of this visual will be able to 
# apply arbitrary transformations to it.
vertex_shader = """
void main() {
   gl_Position = $transform(vec4($position, 0, 1));
}
"""

# Very simple fragment shader. Again we use a template variable "$color", which
# allows us to decide later how the color should be defined (in this case, we
# will just use a uniform red color).
fragment_shader = """
void main() {
  gl_FragColor = $color;
}
"""


# Start the new Visual class. 
# By convention, all Visual subclass names end in 'Visual'.
# (Custom visuals may ignore this convention, but for visuals that are built 
# in to vispy, this is required to ensure that the VisualNode subclasses are 
# generated correctly.)
class MyRectVisual(visuals.Visual):
    """Visual that draws a red rectangle.
    
    Parameters
    ----------
    x : float
        x coordinate of rectangle origin
    y : float
        y coordinate of rectangle origin
    w : float
        width of rectangle
    h : float
        height of rectangle
        
    All parameters are specified in the local (arbitrary) coordinate system of
    the visual. How this coordinate system translates to the canvas will 
    depend on the transformation functions used during drawing.
    """
    
    # There are no constraints on the signature of the __init__ method; use
    # whatever makes the most sense for your visual.
    def __init__(self, x, y, w, h):
        visuals.Visual.__init__(self)
        
        # vertices for two triangles forming a rectangle
        self.vbo = gloo.VertexBuffer(np.array([
            [x, y], [x+w, y], [x+w, y+h],
            [x, y], [x+w, y+h], [x, y+h]
        ], dtype=np.float32))
        
        # We use a ModularProgram because it allows us to plug in arbitrary 
        # transformation functions. This is recommended but not strictly 
        # required.
        self.program = visuals.shaders.ModularProgram(vertex_shader, 
                                                      fragment_shader)
        
        # Assign values to the $position and $color template variables in 
        # the shaders. ModularProgram automatically handles generating the 
        # necessary attribute and uniform declarations with unique variable
        # names.
        self.program.vert['position'] = self.vbo
        self.program.frag['color'] = (1, 0, 0, 1)
        
    # The draw method is required to take a single argument that will be an
    # instance of visuals.transforms.TransformSystem.
    def draw(self, transforms):
        # The TransformSystem provides information about:
        # 
        # * The transformation requested by the user (usually translation, 
        #   rotation, and scaling)
        # * The canvas dpi and the size of logical pixels
        # * The relationship between physical pixels and logical pixels, which
        #   is important for some high-resolution displays and when exporting 
        #   to images
        
        # For the simple case of this visual, all we need to know is how to 
        # convert from the user-specified coordinates (x, y, w, h) to the 
        # normalized device coordinates required by the vertex shader. We will
        # explore other uses of the TransformSystem in later tutorials.
        self.program.vert['transform'] = transforms.get_full_transform()
        
        # Finally, draw the triangles.
        self.program.draw('triangles')


# At this point the visual is ready to use, but it takes some extra effort to
# set up a Canvas and TransformSystem for drawing (the examples in 
# examples/basics/visuals/ all follow this approach). 
# 
# An easier approach is to make the visual usable in a scenegraph, in which 
# case the canvas will take care of drawing the visual and setting up the 
# TransformSystem for us.
# 
# To be able to use our new Visual in a scenegraph, it needs to be
# a subclass of scene.Node. In vispy we achieve this by creating a parallel
# set of classes that inherit from both Node and each Visual subclass.
# This can be done automatically using scene.visuals.create_visual_node():
MyRect = scene.visuals.create_visual_node(MyRectVisual)

# By convention, these classes have the same name as the Visual they inherit 
# from, but without the 'Visual' suffix.

# The auto-generated class MyRect is basically equivalent to::
# 
#     class MyRect(MyRectVisual, scene.Node):
#        def __init__(self, *args, **kwds):
#            parent = kwds.pop('parent', None)
#            name = kwds.pop('name', None)
#            MyRectVisual.__init__(self, *args, **kwds)
#            Node.__init__(self, parent=parent, name=name)
#         


# Finally we will test the visual by displaying in a scene.

# Create a canvas to display our visual
canvas = scene.SceneCanvas(keys='interactive', show=True)

# Create two instances of MyRect, each using canvas.scene as their parent
rects = [MyRect(100, 100, 200, 300, parent=canvas.scene),
         MyRect(500, 100, 200, 300, parent=canvas.scene)]

# To test that the user-specified transforms work correctly, I'll rotate
# one rectangle slightly.
tr = visuals.transforms.AffineTransform()
tr.rotate(5, (0, 0, 1))
rects[1].transform = tr

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
