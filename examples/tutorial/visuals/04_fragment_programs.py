"""
   Tutorial: Creating Visuals
     04. Fragment Programs
--------------------------------

In this tutorial, we will demonstrate the use of the fragment shader as a 
raycaster to draw complex shapes on a simple rectanglular mesh.

Previous tutorials focused on the use of forward transformation functions to 
map vertices from the local coordinate system of the visual to the "render 
coordinates" output of the vertex shader. In this tutorial, we will use inverse
transformation functions in the fragment shader to map backward from the 
current fragment location to the visual's local coordinate system. 
"""

from vispy import app, gloo, visuals, scene
import numpy as np


vertex_shader = """
"""

fragment_shader = """
"""


class MyRectVisual(visuals.Visual):
    """
    """
    
    def __init__(self, x, y, w, h):
        visuals.Visual.__init__(self)
        
        self.program = visuals.shaders.ModularProgram(vertex_shader, 
                                                      fragment_shader)
        
    def draw(self, transforms):
        gloo.set_state(cull_face='front_and_back')
        
        
        # Finally, draw the triangles.
        self.program.draw('triangle_fan')


# As in the previous tutorial, we auto-generate a Visual+Node class for use
# in the scenegraph.
MyRect = scene.visuals.create_visual_node(MyRectVisual)


if __name__ == '__main__':
    canvas = scene.SceneCanvas(keys='interactive', show=True)
    
    # This time we add a ViewBox to let the user zoom/pan
    view = canvas.central_widget.add_view()
    view.camera.rect = (0, 0, 800, 800)

    # ..and optionally start the event loop
    import sys
    if sys.flags.interactive == 0:
        app.run()
