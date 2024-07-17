import numpy as np

import vispy.gloo


class BaseTransferFunction:
    """Base class for transfer functions that applies a colormap to a data value.

    This class may be subclassed to implement more sophisticated transfer functions for raycasting
    volume data.

    To subclass, implement a `applyTransferFunction` function in GLSL. This method takes several
    parameters and must return a `vec4` color value. The parameters are:
        color : vec4
            The color value from the texture.
        loc : vec3
            The location in the volume data (in world coordinates), the exact meaning of this
            depends on the rendering method, but it is conceptually similar to `gl_FragDepth`.
        origin : vec3
            The origin of the ray. In volume rendering, this is a point on a bounding sphere of the
            volume. In plane rendering, this is a point on the surface of the slab.
        step : vec3
            The step vector for the cast ray (direction and length).
        max_depth : float
            The maximum depth the ray may travel from `depth_origin` to `loc`. This is useful for
            normalizing values based on texture depth.
    """

    glsl_tf = """\
    vec4 applyTransferFunction(vec4 color, vec3 loc, vec3 origin, vec3 step, float max_depth) {
        return applyColormap(colorToVal(color));
    }
    """

    def get_glsl(self):
        return self.glsl_tf

    def get_uniforms(self):
        return {}


class TextureSamplingTF(BaseTransferFunction):
    """Transfer function that samples a 2D texture to apply a higher-order colormap to a data value.

    This class may be subclassed to implement more sophisticated transfer functions for raycasting
    volume data.

    For example, a subclass could implement a 2D transfer function that uses the data value and
    gradient magnitude to sample a 2D transfer function.
    """

    glsl_lut = """\
    uniform sampler2D texture2D_TF_LUT;
    vec4 sampleTFLUT(float u, float v) {
        return texture2D(texture2D_TF_LUT, vec2(clamp(u, 0.0, 1.0), clamp(v, 0.0, 1.0)));
    }
    """

    def __init__(self, lut=None):
        super().__init__()
        self._lut = lut

    @property
    def lut(self):
        if self._lut is None:
            return None
        lut = vispy.gloo.Texture2D(self._lut.astype(np.float32, copy=True))
        return lut

    @lut.setter
    def lut(self, lut):
        self._lut = lut

    def get_glsl(self):
        if self._lut is None:
            return self.glsl_tf
        else:
            return self.glsl_lut + self.glsl_tf

    def get_uniforms(self):
        base_uniforms = super().get_uniforms()
        if self._lut is None:
            return base_uniforms
        return base_uniforms | {"texture2D_TF_LUT": self.lut}
