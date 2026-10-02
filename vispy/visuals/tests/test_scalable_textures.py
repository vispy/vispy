import numpy as np
import pytest

from vispy.testing import run_tests_if_main

from vispy.visuals._scalable_textures import (
    get_default_clim_from_dtype,
    get_default_clim_from_data,
    CPUScaledTextureMixin,
    GPUScaledTextureMixin,
)


class Stub:
    _ndim = 2

    def __init__(self, data, **kwargs):
        pass

    def set_data(self, data, *args, **kwargs):
        self._data = data


class CPUScaledStub(CPUScaledTextureMixin, Stub):
    pass


class GPUScaledStub(GPUScaledTextureMixin, Stub):

    internalformat = "r32f"

    def _get_texture_format_for_data(self, data, internalformat=None):
        return None


def test_default_clim():
    ref_data = np.array([10, 5, 15, 25, 15])

    # f32
    data = ref_data.astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)

    # i32
    data = ref_data.astype(np.int32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (-2**31, 2**31 - 1)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)

    # u8
    data = ref_data.astype(np.uint8)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 255)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)


def test_default_clim_non_finite():

    data = np.array([10, np.nan, 5, 15, 25, 15]).astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)

    data = np.array([10, np.inf, 5, 15, 25, 15]).astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)

    data = np.array([10, -np.inf, 5, 15, 25, 15]).astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (5, 25)

    data = np.array([np.nan, np.nan, np.nan]).astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (0, 0)

    data = np.array([np.nan, np.inf, -np.inf]).astype(np.float32)
    clim = get_default_clim_from_dtype(data.dtype)
    assert clim == (0, 1)
    clim = get_default_clim_from_data(data)
    assert clim == (0, 0)


def test_clim_handling_cpu():
    ref_data = np.array([[10, 10, 5], [15, 25, 15]])

    # f32 - auto clim
    st = CPUScaledStub()
    st.set_clim("auto")
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (5, 25)
    assert st.clim_normalized == (0, 1)
    assert np.all(st._data == (ref_data - 5) / 20)

    # Updating clim keeps data the same if not changing too much
    st.set_clim((0, 20))
    assert st.clim == (0, 20)
    assert st.clim_normalized == (-0.25, 0.75)
    assert np.all(st._data == (ref_data - 5) / 20)

    # f32 - custom clim
    st = CPUScaledStub()
    st.set_clim((0, 20))
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (0, 20)
    assert st.clim_normalized == (0, 1)
    assert np.all(st._data == ref_data / 20)

    # f32 - flat clim
    st = CPUScaledStub()
    st.set_clim((10, 10))
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (10, 10)
    assert st.clim_normalized == (0, np.inf)
    # assert np.min(st._data) == 0 - does not matter

    # f32 - auto clim
    st = CPUScaledStub()
    st.set_clim("auto")
    assert st.clim == "auto"
    pytest.raises(RuntimeError, getattr, st, "clim_normalized")
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (5, 25)
    assert st.clim_normalized == (0, 1)

    # u8 auto -> f32 auto
    st = CPUScaledStub()
    st.set_clim("auto")
    assert st.clim == "auto"
    st.scale_and_set_data(ref_data.astype(np.uint8))
    assert st.clim == (5, 25)
    assert st.clim_normalized == (0, 1)
    # set new data with an out-of-range value
    # it should clip at the limits of the original data type
    st.set_clim("auto")
    assert st.clim == "auto"
    new_data = np.array([[10, 10, 5], [15, 2048, 15]], dtype=np.float32)
    st.scale_and_set_data(new_data)
    assert st.clim == (5, 255)
    assert st.clim_normalized == (0, 1)


@pytest.mark.parametrize("clim", ["auto", (5, 25), (10, 10)])
@pytest.mark.parametrize("shape", [(3, 3), (4, 4), (64, 64), (3, 3, 1)])
def test_clim_handling_cpu_nan(clim, shape):
    data = np.full(shape, 15, dtype=np.float32)
    data.flat[0] = 5
    data.flat[-1] = 25
    data.flat[data.size // 2] = np.nan
    original = data.copy()
    data.flags.writeable = False

    st = CPUScaledStub()
    st.set_clim(clim)
    st.scale_and_set_data(data, copy=False)

    expected = original.copy()
    cmin, cmax = (5, 25) if clim == "auto" else clim
    if cmin != cmax:
        expected = (expected - cmin) / (cmax - cmin)
    expected[np.isnan(expected)] = 0
    np.testing.assert_array_equal(st._data, expected)
    np.testing.assert_array_equal(data, original)


def test_clim_handling_cpu_all_nan():
    data = np.full((3, 3), np.nan, dtype=np.float32)
    st = CPUScaledStub()
    st.set_clim("auto")
    st.scale_and_set_data(data, copy=False)
    np.testing.assert_array_equal(st._data, np.zeros_like(data))
    assert np.isnan(data).all()
    assert st.clim == (0, 0)


@pytest.mark.parametrize("copy", [False, True])
def test_cpu_scaling_nan_preserves_infinities(copy):
    data = np.array([[np.nan, -np.inf, np.inf]], dtype=np.float32)
    scaled = CPUScaledTextureMixin._scale_data_on_cpu(data, (0, 1), copy)
    np.testing.assert_array_equal(scaled, [[0, -np.inf, np.inf]])
    assert np.isnan(data[0, 0])


def test_clim_handling_gpu():
    ref_data = np.array([[10, 10, 5], [15, 25, 15]])

    # f32 - auto clim
    st = GPUScaledStub()
    st.set_clim("auto")
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (5, 25)
    assert st.clim_normalized == (5, 25)
    assert np.all(st._data == ref_data)

    # Updating clim keeps data the same if not changing too much
    st.set_clim((0, 20))
    assert st.clim == (0, 20)
    assert st.clim_normalized == (0, 20)
    assert np.all(st._data == ref_data)

    # f32 - custom clim
    st = GPUScaledStub()
    st.set_clim((0, 20))
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (0, 20)
    assert st.clim_normalized == (0, 20)
    assert np.all(st._data == ref_data)

    # f32 - flat clim
    st = GPUScaledStub()
    st.set_clim((10, 10))
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (10, 10)
    assert st.clim_normalized == (10, np.inf)
    # assert np.min(st._data) == 0 - does not matter

    # f32 - auto clim
    st = GPUScaledStub()
    st.set_clim("auto")
    assert st.clim == "auto"
    pytest.raises(RuntimeError, getattr, st, "clim_normalized")
    st.scale_and_set_data(ref_data.astype(np.float32))
    assert st.clim == (5.0, 25.0)
    assert st.clim_normalized == (5.0, 25.0)


run_tests_if_main()
