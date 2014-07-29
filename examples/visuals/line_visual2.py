# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" A Line Visual that uses the new shader Function.
"""

from __future__ import division

import numpy as np

#from .visual import Visual
#from ..shader.function2 import Function, Variable
#from ...import gloo

from vispy.scene.visuals.visual import Visual
from vispy.scene.shaders.function import Function, Variable, Varying
from vispy.scene.shaders.program import ModularProgram
from vispy import gloo


## Snippet templates (defined as string to force user to create fresh Function)
# Consider these stored in a central location in vispy ...


vertex_template = """
void main() {
}
"""

fragment_template = """
void main() {
}
"""


dash_template = """
float dash() {
    float mod = $distance / $dash_len;
    mod = mod - int(mod);
    return 0.5 * sin(mod*3.141593*2) + 0.5;
}
"""
            
## Functions that can be uses as is (don't have template variables)
# Consider these stored in a central location in vispy ...

color3to4 = Function("""
vec4 color3to4(vec3 rgb) {
    return vec4(rgb, 1.0);
}
""")

stub4 = Function("vec4 stub4(vec4 value) { return value; }")
stub3 = Function("vec4 stub3(vec3 value) { return value; }")


## Actual code

class Line(Visual):
    
    def __init__(self, parent, data, color=None):
        Visual.__init__(self, parent)
        
        # Create a program
        self._program = ModularProgram(vertex_template, fragment_template)
        
        # Define how we are going to specify position and color
        self._program.vert['gl_Position'] = 'vec4($position, 1.0)'
        self._program.frag['gl_FragColor'] = 'vec4($color, 1.0)'
        
        # Set position data
        vbo = gloo.VertexBuffer(data)
        self._program.vert['position'] = vbo
        
        # Create some variables related to color. We use a combination
        # of these depending on the kind of color being set.
        # We predefine them here so that we can re-use VBO and uniforms
        vbo = gloo.VertexBuffer(data)
        self._color_var = Variable('uniform vec3 color')
        self._colors_var = Variable('attribute vec3 color', vbo)
        self._color_varying = Varying('v_color')
        
        self.set_color((0, 0, 1))
        if color is not None:
            self.set_color(color)
    
    def set_data(self, data):
        """ Set the vertex data for this line.
        """
        vbo = self._program.vert['position'].value
        vbo.set_data(data)
    
    def set_color(self, color):
        """ Set the color for this line. Color can be specified for the
        whole line or per vertex.
        
        When the color is changed from single color to array, the shaders
        need to be recompiled, otherwise we only need to reset the
        uniform / attribute.
        """
        
        if isinstance(color, tuple):
            # Single value (via a uniform)
            color = [float(v) for v in color]
            assert len(color) == 3
            self._color_var.value = color
            self._program.frag['color'] = self._color_var
        elif isinstance(color, np.ndarray):
            # A value per vertex, via a VBO
            assert color.shape[1] == 3
            self._colors_var.value.set_data(color)
            self._program.frag['color'] = self._color_varying
            self._program.vert[self._color_varying] = self._colors_var
        else:
            raise ValueError('Line colors must be Nx3 array or color tuple')
    
    def draw(self, event=None):
        gloo.set_state(blend=True, blend_func=('src_alpha', 'one'))
        
        # Draw
        self._program.draw('line_strip')


class DashedLine(Line):
    """ This takes the Line and modifies the composition of Functions
    to create a dashing effect.
    """
    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        
        dasher = Function(dash_template) 
        self._program.frag['gl_FragColor.a'] = dasher()
        dasher['distance'] = Varying('v_distance', dtype='float')
        dasher['dash_len'] = '0.001'
        self._program.vert[dasher['distance']] = 'gl_Position.x'


## Show the visual

if __name__ == '__main__':
    from vispy import app
    
    # vertex positions of data to draw
    N = 200
    pos = np.zeros((N, 3), dtype=np.float32)
    pos[:, 0] = np.linspace(-0.9, 0.9, N)
    pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)
    
    # color array
    color = np.ones((N, 3), dtype=np.float32)
    color[:, 0] = np.linspace(0, 1, N)
    color[:, 1] = color[::-1, 0]
    
    class Canvas(app.Canvas):
        def __init__(self):
            app.Canvas.__init__(self, close_keys='escape')
            
            self.line1 = Line(None, pos, (3, 9, 0))
            self.line2 = DashedLine(None, pos + 0.4, color)
    
        def on_draw(self, ev):
            gloo.clear((0, 0, 0, 1), True)
            gloo.set_viewport(0, 0, *self.size)
            self.line1.draw()
            self.line2.draw()
    
    c = Canvas()
    c.show()
    app.run()
