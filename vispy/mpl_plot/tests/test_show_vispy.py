# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from nose.tools import assert_raises

from vispy.io import read_png, load_data_file
from vispy.testing import has_matplotlib, requires_application
import vispy.mpl_plot as plt


@requires_application()
def test_show_vispy():
    """Some basic tests of show_vispy"""
    if has_matplotlib():
        n = 200
        t = np.arange(n)
        noise = np.random.RandomState(0).randn(n)
        # Need, image, markers, line, axes, figure
        plt.figure()
        ax = plt.subplot(211)
        ax.imshow(read_png(load_data_file('pyplot/logo.png')))
        ax = plt.subplot(212)
        ax.plot(t, noise, 'ko-')
        plt.draw()
        canvases = plt.show()
        canvases[0].close()
    else:
        assert_raises(ImportError, plt.show)
