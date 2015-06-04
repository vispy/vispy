
from . import Visual
from .shaders import ModularProgram, Function
from ..color import get_colormap


import numpy as np

VERT_SHADER = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = $transform(vec4(a_position, 0, 1));
}
"""

FRAG_SHADER_FOR_HORIZONTAL = """
varying vec2 v_texcoord;

void main()
{   
    vec4 mapped_color = $color_transform(v_texcoord.x);
    gl_FragColor = mapped_color;
}
"""  # noqa


# TODO:
# * assumes horizontal. allow vertical
# * draw border around rectangle
# * allow border width setting (this will require points in
# pixel coordinates, how do I do that?)
# * actually obey clim
# * write docs for color bar
class ColorBarVisual(Visual):

    def __init__(self, pos, halfdim, cmap, clim, **kwargs):

        super(ColorBarVisual, self).__init__(**kwargs)

        self.cmap = get_colormap(cmap)
        self.clim = clim

        x, y = pos
        halfw, halfh = halfdim

        vertices = np.array([[x - halfw, y - halfh], [x + halfw, y - halfh],
                            [x + halfw, y + halfh],

                            [x - halfw, y - halfh], [x + halfw, y + halfh],
                            [x - halfw, y + halfh]],
                            dtype=np.float32)

        tex_coords = np.array([[0, 0], [1, 0], [1, 0],
                              [0, 0], [1, 0], [0, 0]],
                              dtype=np.float32)

        self.program = ModularProgram(VERT_SHADER, FRAG_SHADER_FOR_HORIZONTAL)

        self.program.frag['color_transform'] = Function(self.cmap.glsl_map)
        self.program['a_position'] = vertices.astype(np.float32)
        self.program['a_texcoord'] = tex_coords.astype(np.float32)

    def draw(self, transforms):
        self.program.vert['transform'] = transforms.get_full_transform()
        self.program.draw('triangles')
