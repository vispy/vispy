import numpy as np
import pytest

from vispy.testing import run_tests_if_main

from vispy.visuals._scalable_textures import (
    get_default_clim_from_dtype,
    get_default_clim_from_data,
    CPUScaledTextureMixin,
    CPUScaledTexture2D,
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


def test_clim_handling_cpu_equal_to_inverted():
    data = np.array([[0, 10]], dtype=np.float32)
    st = CPUScaledStub()
    st.set_clim((5, 5))
    st.scale_and_set_data(data)
    assert st.clim_normalized == (0, np.inf)

    assert st.set_clim((10, 0))
    st.scale_and_set_data(data)
    assert st.clim_normalized == (0, 1)
    assert np.all(st._data == (data - 10) / -10)


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


@pytest.mark.parametrize('dtype', [np.uint8, np.float32])
def test_cpu_texture_finite_storage(dtype):
    data = np.arange(12, dtype=dtype).reshape(3, 4)
    original = data.copy()
    texture = CPUScaledTexture2D(data)
    assert texture.shape[-1] == 1
    texture.set_clim((0, 11))
    texture.scale_and_set_data(data, copy=False)
    assert texture.shape == (3, 4, 1)
    assert texture.format == 'luminance'
    uploaded = texture._glir.clear()[-1][3]
    np.testing.assert_allclose(uploaded[..., 0], original / 11, rtol=1e-6)
    np.testing.assert_allclose(data, original, rtol=0, atol=0)


@pytest.mark.parametrize('shape', [(3, 4), (3, 4, 1)])
def test_cpu_texture_nan_storage(shape):
    data = np.ones(shape, dtype=np.float32)
    texture = CPUScaledTexture2D(data)
    texture.set_clim((0, 2))
    for has_nan in (False, True, False):
        data[0, 0] = np.nan if has_nan else 1
        original = data.copy()
        texture.scale_and_set_data(data, copy=False)
        assert texture.shape == (3, 4, 2 if has_nan else 1)
        uploaded = texture._glir.clear()[-1][3]
        expected = np.full((3, 4), 0.5, dtype=np.float32)
        if has_nan:
            expected[0, 0] = 0
            np.testing.assert_array_equal(uploaded[..., 1], ~np.isnan(data.reshape(3, 4)))
        np.testing.assert_allclose(uploaded[..., 0], expected, rtol=1e-6)
        np.testing.assert_allclose(data, original, rtol=0, atol=0, equal_nan=True)


@pytest.mark.parametrize('has_nan', [False, True])
def test_cpu_texture_offset_keeps_layout(has_nan):
    data = np.ones((3, 4), dtype=np.float32)
    if has_nan:
        data[0, 0] = np.nan
    texture = CPUScaledTexture2D(data)
    texture.set_clim((0, 2))
    texture.scale_and_set_data(data, copy=False)
    assert texture.shape[-1] == (2 if has_nan else 1)
    texture._glir.clear()

    for patch in (np.array([[np.nan, 1]], dtype=np.float32),
                  np.array([[1, 0]], dtype=np.float32)):
        original = patch.copy()
        texture.scale_and_set_data(patch, offset=(1, 1), copy=False)
        assert texture.shape == (3, 4, 2 if has_nan else 1)
        commands = texture._glir.clear()
        assert len(commands) == 1
        command, texture_id, offset, uploaded = commands[0]
        assert command == 'DATA'
        assert offset == (1, 1)
        assert uploaded.shape == (1, 2, 2 if has_nan else 1)
        expected = original / 2
        if has_nan:
            np.testing.assert_array_equal(uploaded[..., 1], ~np.isnan(original))
            expected = np.nan_to_num(expected)
        np.testing.assert_allclose(uploaded[..., 0], expected, rtol=1e-6, equal_nan=True)
        np.testing.assert_allclose(patch, original, rtol=0, atol=0, equal_nan=True)


run_tests_if_main()
