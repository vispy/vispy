from vispy.gloo import Texture2D, VertexBuffer
from vispy.visuals.shaders import Function, Varying
import numpy as np


class TextureFilter(object):

    def __init__(self, texture, texcoords):
        self.texture = texture
        self.texcoords = texcoords
        self._texcoords = VertexBuffer(np.zeros((0, 2), dtype=np.float32))
        self._texcoord_varying = Varying('v_texcoord', 'vec2')
        self.apply_coords = Function("""
            void apply_coords() {
                $v_texcoords = $texcoords;
            }
        """)

        self.apply_texture = Function("""
            void apply_texture() {
                gl_FragColor *= texture2D($u_texture, $texcoord);
            }
        """)

        self.coords_expr = self.apply_coords()
        self.texture_expr = self.apply_texture()

    def _attach(self, visual):
        # vertex shader
        vert_pre = visual._get_hook('vert', 'pre')
        vert_pre.add(self.coords_expr)
        tc = self.texcoords[visual.mesh_data.get_faces()]
        self._texcoords.set_data(tc, convert=True)
        self.apply_coords['texcoords'] = self._texcoords
        self.apply_coords['v_texcoords'] = self._texcoord_varying

        # fragment shader
        frag_post = visual._get_hook('frag', 'post')
        frag_post.add(self.texture_expr)
        self.apply_texture['texcoord'] = self._texcoord_varying
        self.apply_texture['u_texture'] = Texture2D(self.texture)

    def _detach(self, visual):
        visual._get_hook('vert', 'pre').remove(self.coords_expr)
        visual._get_hook('frag', 'post').remove(self.texture_expr)
