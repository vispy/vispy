# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy.pyplot import show_vispy
import matplotlib.pyplot as plt

n = 100
x = np.linspace(-1.0, +1.0, n)
y = np.random.uniform(-0.5, +0.5, n)
fig, ax = plt.subplots()
ax.plot(x, y, 'r-o')
# idx = np.argmax(y)
# ax.text(x[idx], y[idx], 'Maximum')
canvas = show_vispy(fig)
