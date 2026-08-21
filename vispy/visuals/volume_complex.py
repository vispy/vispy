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

        if not np.iscomplexobj(vol):
            raise ValueError('Data must be complex. Use VolumeVisual instead.')
        self._complex_mode = complex_mode

        if kwargs.get("clim", "auto") == "auto":
            kwargs["clim"] = self._calc_complex_clim(vol)

        kwargs["texture_format"] = "rg32f"
        self._in_init = True
        vol = self._convert_complex_to_float_view(vol)
        super().__init__(vol, **kwargs)

    def set_data(self, vol, clim=None, copy=True):
        vol = np.asarray(vol)
        if not self._in_init:
            vol = self._convert_complex_to_float_view(vol)

        if clim is not None and clim != self._texture.clim:
            self._texture.set_clim(clim)

        # Apply to texture
        self._texture.check_data_format(vol)
        self._last_data = vol
        self._texture.scale_and_set_data(vol, copy=copy)
        self.shared_program['clim'] = self._texture.clim_normalized
        self.shared_program['u_shape'] = (vol.shape[2], vol.shape[1],
                                          vol.shape[0])
        self._is_rgb = False
        self.shared_program['u_rgb_mode'] = False

        shape = vol.shape[:3]
        if self._vol_shape != shape:
            self._vol_shape = shape
            self._need_vertex_update = True
        self._vol_shape = shape

    @property
    def complex_mode(self):
        return self._complex_mode

    @complex_mode.setter
    def complex_mode(self, value):
        if value not in self.COMPLEX_MODES:
            raise ValueError(
                f'complex_mode must be one of {", ".join(self.COMPLEX_MODES)}'
            )

        if self._complex_mode != value:
            self._complex_mode = value
            self.shared_program.frag['colorToScalar'] = self._color_to_scalar_snippet
            self.update()

    @property
    def _color_to_scalar_snippet(self):
        return Function(COMPLEX_TRANSFORMS[self.complex_mode])

    @staticmethod
    def _convert_complex_to_float_view(complex_arr):
        # turn complex128 into complex64 if needed
        complex64_arr = complex_arr.astype(np.complex64, copy=False)
        float_view_arr = complex64_arr.view(dtype=np.float32).reshape((complex64_arr.shape + (2, )))
        return float_view_arr

    @property
    def clim(self):
        """The contrast limits that were applied to the volume data.

        Volume display is mapped from black to white with these values.
        Settable via set_data() as well as @clim.setter.
        """
        return self._texture.clim

    @clim.setter
    def clim(self, value):
        """Set contrast limits used when rendering the image.

        ``value`` should be a 2-tuple of floats (min_clim, max_clim), where each value is
        within the range set by self.clim. If the new value is outside of the (min, max)
        range of the clims previously used to normalize the texture data, then data will
        be renormalized using set_data.
        """
        if value == "auto" and self.complex_mode:
            value = self._calc_complex_clim()
        if self._texture.set_clim(value):
            self.set_data(self._last_data, clim=value)
        self.shared_program['clim'] = self._texture.clim_normalized
        self.update()

    def _calc_complex_clim(self, data=None):
        # it would be nice if this could be done in the scalable texture mixin,
        # but that would require the mixin knowing about the complex mode.
        func = CPU_COMPLEX_TRANSFORMS[self.complex_mode]
        _rendered = func(self._data if data is None else data)
        return (_rendered.min(), _rendered.max())
