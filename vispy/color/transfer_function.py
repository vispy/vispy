import numpy as np

import vispy.gloo


class BaseTransferFunction:
    """Class representing a 2D transfer function.

    Parameters
    ----------
    lut : array-like
        Lookup table for the transfer function. This may be None (default) if
        the transfer function can compute colors directly.
    """
    glsl_tf = """\
    vec4 applyTransferFunction(vec4 color, vec3 loc, vec3 start_loc, vec3 step) {
        return applyColormap(colorToVal(color));
    }
    """

    def get_glsl(self):
        return self.glsl_tf

    def get_uniforms(self):
        return {}


class TextureSamplingTF(BaseTransferFunction):
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
        if self._lut is None:
            return {}
        else:
            return {"texture2D_TF_LUT": self.lut}
