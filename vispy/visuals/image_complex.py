from .image import ImageVisual, _apply_clim_float, _apply_gamma_float
import numpy as np
from .shaders import Function, FunctionChain

_complex_mag = """
    float comp2float(vec4 data) {
        return sqrt(data.r * data.r + data.g * data.g);
    }"""
_complex_angle = """
    float comp2float(vec4 data) {
        return atan(data.g, data.r);
    }"""
_complex_real = """
    float comp2float(vec4 data) {
        return data.r;
    }"""
_complex_imaginary = """
    float comp2float(vec4 data) {
        return data.g;
    }"""

COMPLEX_TRANSFORMS = {
    "magnitude": _complex_mag,
    "phase": _complex_angle,
    "real": _complex_real,
    "imaginary": _complex_imaginary,
}


class ComplexImageVisual(ImageVisual):
    COMPLEX_MODES = set(COMPLEX_TRANSFORMS)

    def __init__(self, data=None, complex_mode="magnitude", **kwargs):
        self._data_is_complex = False
        if complex_mode not in self.COMPLEX_MODES:
            raise ValueError(
                "complex_mode must be one of %s" % ", ".join(self.COMPLEX_MODES)
            )
        self._complex_mode = complex_mode
        kwargs['texture_format'] = 'auto'
        super().__init__(data=data, **kwargs)

    def set_data(self, image):
        data = np.asarray(image)
        self._data_is_complex = np.iscomplexobj(data)
        if self._data_is_complex:
            # even though we're only ever using the first and/or second channels,
            # without the third empty "channel", it doesn't render correctly.
            # could be a bug in rg32f rendering?
            data = np.stack(
                [data.real, data.imag, np.empty_like(data, np.float32)], axis=-1
            )
        return super().set_data(data)

    @property
    def complex_mode(self):
        return self._data_is_complex and self._complex_mode

    @complex_mode.setter
    def complex_mode(self, value):
        if value not in self.COMPLEX_MODES:
            raise ValueError(
                "complex_mode must be one of %s" % ", ".join(self.COMPLEX_MODES)
            )
        if self._complex_mode != value:
            self._complex_mode = value
            self._need_colortransform_update = True
            self.update()

    def _build_color_transform(self):
        if self.complex_mode:
            fclim = Function(_apply_clim_float)
            fgamma = Function(_apply_gamma_float)
            chain = [
                Function(COMPLEX_TRANSFORMS[self.complex_mode]),
                fclim,
                fgamma,
                Function(self.cmap.glsl_map),
            ]
            fun = FunctionChain(None, chain)
            fclim["clim"] = self._texture.clim_normalized
            fgamma["gamma"] = self.gamma
            return fun
        return super()._build_color_transform()
