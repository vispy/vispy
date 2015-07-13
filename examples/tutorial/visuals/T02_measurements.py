# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Tutorial: Creating Visuals
==========================

02. Making physical measurements
--------------------------------

In the last tutorial we created a simple Visual subclass that draws a 
rectangle. In this tutorial, we will make two additions:

    1. Draw a rectangular border instead of a solid rectangle
    2. Make the border a fixed pixel width, even when displayed inside a 
       user-zoomable ViewBox. 

The border is made by drawing a line_strip with 10 vertices::

    1--------------3
    |              |
    |   2------4   |     [ note that points 9 and 10 are
    |   |      |   |       the same as points 1 and 2 ]
    |   8------6   |
    |              |
    7--------------5

In order to ensure that the border has a fixed width in pixels, we need to 
adjust the spacing between the inner and outer rectangles whenever the user
changes the zoom of the ViewBox.

How? Recall that each 
time the visual is drawn, it is given a TransformSystem instance that carries
information about the size of logical and physical pixels relative to the 
visual [link to TransformSystem documentation]. Essentially, we have 4 
coordinate systems:

    Visual -> Document -> Framebuffer -> Render
    
The user specifies the position and size of the rectangle in Visual 
coordinates, and in [tutorial 1] we used the vertex shader to convert directly
from Visual coordinates to render coordinates. In this tutorial we will
convert first to document coordinates, then make the adjustment for the border
width, then convert the remainder of the way to render coordinates.

Let's say, for example that the user specifies the box width to be 20, and the 
border width to be 5. To draw the border correctly, we cannot simply 
add/subtract 5 from the inner rectangle coordinates; if the user zooms 
in by a factor of 2 then the border would become 10 px wide.

Another way to say this is that a vector with length=1 in Visual coordinates
does not _necessarily_ have a length of 1 pixel on the canvas. Instead, we must
make use of the Document coordinate system, in which a vector of length=1
does correspond to 1 pixel.

There are a few ways we could make this measurement of pixel length. Here's
how we'll do it in this tutorial:

    1. Begin with vertices for a rectangle with border width 0 (that is, vertex
       1 is the same as vertex 2, 3=4, and so on).
    2. In the vertex shader, first map the vertices to the document coordinate
       system using the visual->document transform.
    3. Add/subtract the line width from the mapped vertices.
    4. Map the rest of the way to render coordinates with a second transform:
       document->framebuffer->render.

Note that this problem _cannot_ be solved using a simple scale factor! It is
necessary to use these transformations in order to draw correctly when there
is rotation or anosotropic scaling involved.

"""
from vispy import app, gloo, visuals, scene
import numpy as np


vertex_shader = """
void main() {
    // First map the vertex to document coordinates
    vec4 doc_pos = $visual_to_doc(vec4($position, 0, 1));
    
    // Also need to map the adjustment direction vector, but this is tricky!
    // We need to adjust separately for each component of the vector:
    vec4 adjusted;
    if ( $adjust_dir.x == 0 ) {
        // If this is an outer vertex, no adjustment for line weight is needed.
        // (In fact, trying to make the adjustment would result in no
        // triangles being drawn, hence the if/else block)
        adjusted = doc_pos;
    }
    else {
        // Inner vertexes must be adjusted for line width, but this is
        // surprisingly tricky given that the rectangle may have been scaled 
        // and rotated!
        vec4 doc_x = $visual_to_doc(vec4($adjust_dir.x, 0, 0, 0)) - 
                    $visual_to_doc(vec4(0, 0, 0, 0));
        vec4 doc_y = $visual_to_doc(vec4(0, $adjust_dir.y, 0, 0)) - 
                    $visual_to_doc(vec4(0, 0, 0, 0));
        doc_x = normalize(doc_x);
        doc_y = normalize(doc_y);
                        
        // Now doc_x + doc_y points in the direction we need in order to 
        // correct the line weight of _both_ segments, but the magnitude of
        // that correction is wrong. To correct it we first need to 
        // measure the width that would result from using doc_x + doc_y:
        vec4 proj_y_x = dot(doc_x, doc_y) * doc_x;  // project y onto x
        float cur_width = length(doc_y - proj_y_x);  // measure current weight
        
        // And now we can adjust vertex position for line width:
        adjusted = doc_pos + ($line_width / cur_width) * (doc_x + doc_y);
    }
    
    // Finally map the remainder of the way to render coordinates
    gl_Position = $doc_to_render(adjusted);
}
"""

fragment_shader = """
void main() {
    gl_FragColor = $color;
}
"""


class MyRectVisual(visuals.Visual):
    """Visual that draws a rectangular outline.
    
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
    weight : float
        width of border (in px)
    """
    
    def __init__(self, x, y, w, h, weight=4.0):
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)
        
        # 10 vertices for 8 triangles (using triangle_strip) forming a 
        # rectangular outline
        self.vert_buffer = gloo.VertexBuffer(np.array([
            [x, y], 
            [x, y], 
            [x+w, y], 
            [x+w, y], 
            [x+w, y+h],
            [x+w, y+h],
            [x, y+h],
            [x, y+h],
            [x, y], 
            [x, y], 
        ], dtype=np.float32))
        
        # Direction each vertex should move to correct for line width
        # (the length of this vector will be corrected in the shader)
        self.adj_buffer = gloo.VertexBuffer(np.array([
            [0, 0],
            [1, 1],
            [0, 0],
            [-1, 1],
            [0, 0],
            [-1, -1],
            [0, 0],
            [1, -1],
            [0, 0],
            [1, 1],
        ], dtype=np.float32))
        
        self.shared_program.vert['position'] = self.vert_buffer
        self.shared_program.vert['adjust_dir'] = self.adj_buffer
        self.shared_program.vert['line_width'] = weight
        self.shared_program.frag['color'] = (1, 0, 0, 1)
        self.set_gl_state(cull_face=False)
        self._draw_mode = 'triangle_strip'

    def _prepare_transforms(self, view):
        # Set the two transforms required by the vertex shader:
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['visual_to_doc'] = tr.get_transform('visual', 'document')
        view_vert['doc_to_render'] = tr.get_transform('document', 'render')


# As in the previous tutorial, we auto-generate a Visual+Node class for use
# in the scenegraph.
MyRect = scene.visuals.create_visual_node(MyRectVisual)


# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True)

# This time we add a ViewBox to let the user zoom/pan
view = canvas.central_widget.add_view()
view.camera = 'panzoom'
view.camera.rect = (0, 0, 800, 800)

# ..and add the rects to the view instead of canvas.scene
rects = [MyRect(100, 100, 200, 300, parent=view.scene),
         MyRect(500, 100, 200, 300, parent=view.scene)]

# Again, rotate one rectangle to ensure the transforms are working as we
# expect.
tr = visuals.transforms.MatrixTransform()
tr.rotate(25, (0, 0, 1))
rects[1].transform = tr

# Add some text instructions
text = scene.visuals.Text("Drag right mouse button to zoom.", color='w',
                          anchor_x='left', parent=view, pos=(20, 30))

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
