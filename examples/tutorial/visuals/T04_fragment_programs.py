"""
Tutorial: Creating Visuals
==========================

04. Fragment Programs
---------------------

In this tutorial, we will demonstrate the use of the fragment shader as a 
raycaster to draw complex shapes on a simple rectanglular mesh.

Previous tutorials focused on the use of forward transformation functions to 
map vertices from the local coordinate system of the visual to the "render 
coordinates" output of the vertex shader. In this tutorial, we will use inverse
transformation functions in the fragment shader to map backward from the 
current fragment location to the visual's local coordinate system. 
"""
import numpy as np
from vispy import app, gloo, visuals, scene


vertex_shader = """
void main() {
   gl_Position = vec4($position, 0, 1);
}
"""

fragment_shader = """
void main() {
  vec4 pos = $fb_to_visual(gl_FragCoord);
  gl_FragColor = vec4(sin(pos.x / 10.), sin(pos.y / 10.), 0, 1);
}
"""


class MyRectVisual(visuals.Visual):
    """
    """
    
    def __init__(self):
        visuals.Visual.__init__(self)
        self.vbo = gloo.VertexBuffer(np.array([
            [-1, -1], [1, -1], [1, 1],
            [-1, -1], [1, 1], [-1, 1]
        ], dtype=np.float32))
        self.program = visuals.shaders.ModularProgram(vertex_shader, 
                                                      fragment_shader)
        self.program.vert['position'] = self.vbo
        
    def draw(self, transforms):
        gloo.set_state(cull_face=False)
        
        tr = (transforms.visual_to_document * 
              transforms.document_to_framebuffer).inverse
        self.program.frag['fb_to_visual'] = tr
                
        # Finally, draw the triangles.
        self.program.draw('triangle_fan')


# As in the previous tutorial, we auto-generate a Visual+Node class for use
# in the scenegraph.
MyRect = scene.visuals.create_visual_node(MyRectVisual)


# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True)

# This time we add a ViewBox to let the user zoom/pan
view = canvas.central_widget.add_view()
view.camera = 'panzoom'
view.camera.rect = (0, 0, 800, 800)

vis = MyRect()
view.add(vis)

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
