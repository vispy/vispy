# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from vispy.pyplot import mpl_to_vispy
from vispy.util import read_png, get_data_file
from vispy.testing import requires_mplexporter, requires_application


@requires_application()
@requires_mplexporter()
def test_show_vispy():
    """Some basic tests of show_vispy"""
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    n = 200
    t = np.arange(n)
    noise = np.random.RandomState(0).randn(n)
    # Need, image, markers, line, axes, figure
    fig = plt.figure()
    ax = plt.subplot(211)
    ax.imshow(read_png(get_data_file('pyplot/logo.png')))
    ax = plt.subplot(212)
    ax.plot(t, noise, 'ko-')
    plt.draw()
    canvas = mpl_to_vispy(fig, block=False)
    canvas.close()
