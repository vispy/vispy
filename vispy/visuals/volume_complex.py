from .volume import VolumeVisual
import numpy as np
from .shaders import Function, FunctionChain

# In a complex Image, the texture will be rg32f, where:
# data.r contains the real component
# data.g contains the imaginary component
COMPLEX_TRANSFORMS = {
    "real": "float cplx2float(vec4 data) { return data.r; }",
    "imaginary": "float cplx2float(vec4 data) { return data.g; }",
    "magnitude": "float cplx2float(vec4 data) { return length(data.rg); }",
    "phase": "float cplx2float(vec4 data) { return atan(data.g, data.r); }",
}
COMPLEX_GRADIENTS = {
    "real": "float colorsToGradient(vec4 c1, vec4 c2) { return c1.r - c2.r; }",
    "imaginary": "float colorsToGradient(vec4 c1, vec4 c2) { return c1.g - c2.g; }",
    "magnitude": "float colorsToGradient(vec4 c1, vec4 c2) { return length(c1.rg) - length(c2.rg); }",
    # the whole gradient machinery is for this: the phase wraps around, so to avoid artifacts
    # at the -pi/+pi edges, we need a gradient calculation that wraps around smoothly
    "phase": (
        "float colorsToGradient(vec4 c1, vec4 c2) {"
        "  float p1 = atan(c1.g, c1.r);"
        "  float p2 = atan(c2.g, c2.r);"
        "  return atan(sin(p1 - p2), cos(p1 - p2));"
        "}"
    ),
}
CPU_COMPLEX_TRANSFORMS = {
    "magnitude": np.abs,
    "phase": np.angle,
    "real": np.real,
    "imaginary": np.imag,
}


class ComplexVolumeVisual(VolumeVisual):
    """:class:`~vispy.visuals.ImageVisual` subclass displaying a complex-valued image.

    This class handles complex values by using an rg32f float texture behind the scenes,
    storing the real component in the "r"  value and the imaginary in the "g" value.

    Parameters
    ----------
    data : ndarray
        Complex valued ImageVisual data.  Should be a two dimensional array with a dtype
        of np.complex64 or np.complex128.
    complex_mode : str
        The mode used to convert the complex value in each pixel into a scalar:
            * 'real': show only the real component.
            * 'imaginary': show only the imaginary component.
            * 'magnitude': show the magnitude (`np.abs`) of the complex value.
            * 'phase': show the phase (`np.angle`) of the complex value.
    """

    COMPLEX_MODES = set(COMPLEX_TRANSFORMS)

    def __init__(self, vol, complex_mode="magnitude", **kwargs):
        if complex_mode not in self.COMPLEX_MODES:
            raise ValueError(
                f'complex_mode must be one of {", ".join(self.COMPLEX_MODES)}'
            )

        self._data_is_complex = np.iscomplexobj(vol)
        self._complex_mode = complex_mode

        if kwargs.get("clim", "auto") == "auto" and self._data_is_complex:
            kwargs["clim"] = self._calc_complex_clim(vol)

        if self._data_is_complex:
            kwargs["texture_format"] = "rg32f"
            vol = self._convert_complex_to_float_view(vol)
        super().__init__(vol, **kwargs)

    def _create_texture(self, texture_format, data, **texture_kwargs):
        if self._data_is_complex:
            texture_kwargs["format"] = "rg"
        return super()._create_texture(texture_format, data, **texture_kwargs)

    def set_data(self, vol, clim=None, copy=True):
        vol = np.asarray(vol)
        if np.iscomplexobj(vol):
            #  Turn the texture into an rg32f texture
            # where r = 'real' and g = 'imag'
            self._data_is_complex = True
            # FUTURE: Add formal way of defining texture format from set_data
            self._texture._format = "rg"
            vol = self._convert_complex_to_float_view(vol)
        elif vol.ndim == 4 and vol.shape[-1] == 2:
            # data was complex but was already converted to 32-bit float
            # should really only occur from __init__
            self._data_is_complex = True
        else:
            self._texture._format = None
        return super().set_data(vol, clim=clim, copy=copy)

    @staticmethod
    def _convert_complex_to_float_view(complex_arr):
        # turn complex128 into complex64 if needed
        complex64_arr = complex_arr.astype(np.complex64, copy=False)
        float_view_arr = complex64_arr.view(dtype=np.float32).reshape((complex64_arr.shape + (2, )))
        return float_view_arr

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
            self._need_interpolation_update = True
            self.update()

    @property
    def _color_to_scalar_snippet(self):
        return Function(COMPLEX_TRANSFORMS[self.complex_mode]) if self._data_is_complex else super()._color_to_scalar_snippet

    @property
    def _colors_to_gradient_snippet(self):
        return Function(COMPLEX_GRADIENTS[self.complex_mode]) if self._data_is_complex else super()._colors_to_gradient_snippet

    @VolumeVisual.clim.setter
    def clim(self, clim):
        if clim == "auto" and self.complex_mode:
            clim = self._calc_complex_clim()
        super(VolumeVisual, type(self)).clim.fset(self, clim)

    def _calc_complex_clim(self, data=None):
        # it would be nice if this could be done in the scalable texture mixin,
        # but that would require the mixin knowing about the complex mode.
        func = CPU_COMPLEX_TRANSFORMS[self.complex_mode]
        _rendered = func(self._data if data is None else data)
        return (_rendered.min(), _rendered.max())
