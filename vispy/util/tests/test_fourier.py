# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from vispy.util.fourier import stft, fft_freqs
from vispy.testing import assert_raises, run_tests_if_main


def test_stft():
    """Test STFT calculation"""
    assert_raises(ValueError, stft, 0)
    assert_raises(ValueError, stft, [], window='foo')
    assert_raises(ValueError, stft, [[]])
    result = stft([])
    assert np.allclose(result, np.zeros_like(result))
    n_fft = 256
    step = 128
    for n_samples, n_estimates in ((256, 1),
                                   (383, 1), (384, 2),
                                   (511, 2), (512, 3)):
        result = stft(np.ones(n_samples), n_fft=n_fft, step=step, window=None)
        assert result.shape[1] == n_estimates
        expected = np.zeros(n_fft // 2 + 1)
        expected[0] = 1
        for res in result.T:
            assert np.allclose(expected, np.abs(res))
            assert np.allclose(expected, np.abs(res))
    for n_pts, last_freq in zip((256, 255), (500., 498.)):
        freqs = fft_freqs(n_pts, 1000)
        assert freqs[0] == 0
        assert np.allclose(freqs[-1], last_freq, atol=1e-1)

run_tests_if_main()
