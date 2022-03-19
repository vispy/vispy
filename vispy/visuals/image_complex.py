from .image import ImageVisual, _APPLY_CLIM_FLOAT, _APPLY_GAMMA_FLOAT
import numpy as np
from .shaders import Function, FunctionChain

# In a complex Image, the texture will be rg32f, where:
# data.r contains the real component
# data.g contains the imaginary component
COMPLEX_TRANSFORMS = {
    "real": "float cplx2float(vec4 data) { return data.r; }",
    "imaginary": "float cplx2float(vec4 data) { return data.g; }",
    "magnitude": "float cplx2float(vec4 data) { return length(data); }",
    "phase": "float cplx2float(vec4 data) { return atan(data.g, data.r); }",
}


class ComplexImageVisual(ImageVisual):
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

    def __init__(self, data=None, complex_mode="magnitude", **kwargs):
        if complex_mode not in self.COMPLEX_MODES:
            raise ValueError(
                "complex_mode must be one of %s" % ", ".join(self.COMPLEX_MODES)
            )
        self._data_is_complex = np.iscomplexobj(data)
        self._complex_mode = complex_mode

        if kwargs.get("clim", "auto") == "auto" and self._data_is_complex:
            kwargs["clim"] = self._calc_complex_clim(data)

        kwargs["texture_format"] = "auto"
        super().__init__(data=data, **kwargs)

    def set_data(self, image):
        data = np.asarray(image)
        self._data_is_complex = np.iscomplexobj(data)
        if self._data_is_complex:
            #  Turn the texture into an rg32f texture
            # where r = 'real' and g = 'imag'
            self._texture._format = "rg"
            # turn complex128 into complex64 if needed
            data = data.astype(np.complex64, copy=False)
            data = data.view(dtype=np.float32).reshape((data.shape + (2, )))
        else:
            self._texture._format = None
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
            fclim = Function(_APPLY_CLIM_FLOAT)
            fgamma = Function(_APPLY_GAMMA_FLOAT)
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

    @ImageVisual.clim.setter
    def clim(self, clim):
        if clim == "auto":
            clim = self._calc_complex_clim()
        super(ComplexImageVisual, type(self)).clim.fset(self, clim)

    def _calc_complex_clim(self, data=None):
        # it would be nice if this could be done in the scalable texture mixin,
        # but that would require the mixin knowing about the complex mode.
        func = {
            "magnitude": np.abs,
            "phase": np.angle,
            "real": np.real,
            "imaginary": np.imag,
        }[self.complex_mode]
        _rendered = func(self._data if data is None else data)
        return (_rendered.min(), _rendered.max())
