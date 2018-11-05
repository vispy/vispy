import numpy as np
from vispy.gloo import Texture2D, VertexBuffer
from vispy.visuals.shaders import Function, Varying


class TextureFilter(object):

    def __init__(self, texture, texcoords, enabled=True):
        """Apply a texture on a mesh.

        Parameters
        ----------
        texture : (M, N) or (M, N, C) array
            The 2D texture image.
        texcoords : (N, 2) array
            The texture coordinates.
        enabled : bool
            Whether the display of the texture is enabled.
        """
        self.pass_coords = Function("""
            void pass_coords() {
                $v_texcoords = $texcoords;
            }
        """)
        self.apply_texture = Function("""
            void apply_texture() {
                if ($enabled == 1) {
                    gl_FragColor *= texture2D($u_texture, $texcoords);
                }
            }
        """)
        self._texcoord_varying = Varying('v_texcoord', 'vec2')
        self.pass_coords['v_texcoords'] = self._texcoord_varying
        self.apply_texture['texcoords'] = self._texcoord_varying
        self._texcoords_buffer = VertexBuffer(
            np.zeros((0, 2), dtype=np.float32)
        )
        self.pass_coords['texcoords'] = self._texcoords_buffer
        self.coords_expr = self.pass_coords()
        self.texture_expr = self.apply_texture()

        self._attached = False
        self._visual = None

        self.enabled = enabled
        self.texture = texture
        self.texcoords = texcoords

    @property
    def enabled(self):
        """True to display the texture, False to disable."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self.apply_texture['enabled'] = 1 if enabled else 0

    @property
    def texture(self):
        """The texture image."""
        return self._texture

    @texture.setter
    def texture(self, texture):
        self._texture = texture
        self.apply_texture['u_texture'] = Texture2D(texture)

    @property
    def texcoords(self):
        """The texture coordinates as an (N, 2) array of floats."""
        return self._texcoords

    @texcoords.setter
    def texcoords(self, texcoords):
        self._texcoords = texcoords
        self._update_texcoords_buffer(texcoords)

    def _update_texcoords_buffer(self, texcoords):
        if not self._attached or self._visual is None:
            return

        # FIXME: Indices for texture coordinates might be different than face
        # indices, although in some cases they are the same. Currently,
        # vispy.io.read_mesh assumes face indices and texture coordinates are
        # the same.
        # TODO:
        # 1. Add reading and returning of texture coordinate indices in
        #    read_mesh.
        # 2. Add texture coordinate indices in MeshData from
        #    vispy.geometry.meshdata
        # 3. Use mesh_data.get_texcoords_indices() here below.
        tc = texcoords[self._visual.mesh_data.get_faces()]
        self._texcoords_buffer.set_data(tc, convert=True)

    def _attach(self, visual):
        vert_pre = visual._get_hook('vert', 'pre')
        vert_pre.add(self.coords_expr)

        frag_post = visual._get_hook('frag', 'post')
        frag_post.add(self.texture_expr)

        self._attached = True
        self._visual = visual

        self._update_texcoords_buffer(self._texcoords)

    def _detach(self, visual):
        visual._get_hook('vert', 'pre').remove(self.coords_expr)
        visual._get_hook('frag', 'post').remove(self.texture_expr)
        self._attached = False
        self._visual = None
