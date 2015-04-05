# -*- coding: utf-8 -*-
import numpy as np

from vispy.scene.visuals import Spectrogram
from vispy.testing import (requires_application, TestingCanvas,
                           assert_image_equal, run_tests_if_main)


@requires_application()
def test_spectrogram():
    """Test spectrogram visual"""
    n_fft = 256
    n_freqs = n_fft // 2 + 1
    size = (100, n_freqs)
    with TestingCanvas(size=size) as c:
        data = np.ones(n_fft * 100)
        spec = Spectrogram(data, n_fft=n_fft, step=n_fft, window=None,
                           color_scale='linear', cmap='grays')
        c.draw_visual(spec)
        expected = np.zeros(size[::-1] + (3,))
        expected[0] = 1.
        assert_image_equal("screenshot", expected)
        freqs = spec.freqs
        assert len(freqs) == n_freqs
        assert freqs[0] == 0
        assert freqs[-1] == 0.5

run_tests_if_main()
