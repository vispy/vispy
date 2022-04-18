from vispy.scene.visuals import ComplexImage
from vispy.visuals.image_complex import CPU_COMPLEX_TRANSFORMS
from vispy.testing import requires_application, TestingCanvas
from vispy.testing.image_tester import downsample

import numpy as np
import pytest

from vispy.testing.rendered_array_tester import compare_render


# we add the np.float32 case to test that ComplexImage falls back to Image behavior
# if the data is not complex
@requires_application()
@pytest.mark.parametrize("input_dtype", [np.complex64, np.complex128, np.float32])
@pytest.mark.parametrize("complex_mode", ["magnitude", "real", "imaginary", "phase"])
def test_image_complex(input_dtype, complex_mode):
    """Test rendering of complex-valued image data."""
    shape = (40, 40)
    np.random.seed(0)
    data = np.random.random(shape).astype(input_dtype)
    if np.iscomplexobj(data):
        data.imag = np.random.random(shape)

    with TestingCanvas(size=shape, bgcolor="w") as c:
        ComplexImage(data, cmap="grays", complex_mode=complex_mode, parent=c.scene)
        # render to canvas
        rendered = c.render()
        shape_ratio = rendered.shape[0] // data.shape[0]
        rendered = downsample(rendered, shape_ratio, axis=(0, 1))

        # perform (auto-clim) rendering on cpu
        exp = CPU_COMPLEX_TRANSFORMS[complex_mode](data) if np.iscomplexobj(data) else data
        exp -= exp.min()
        exp /= exp.max()
        compare_render(exp, rendered)
