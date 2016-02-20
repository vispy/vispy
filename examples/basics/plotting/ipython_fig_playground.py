#!/usr/bin/env ipython -i ipython_fig_playground.py
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Bare bones plotting region that can be used with the python
interpreter as a playground.

Run with
python -i ipython_fig_playground.py
"""
from vispy import plot as vp  # noqa
import numpy as np  # noqa

fig = vp.Fig(size=(600, 500))  # noqa
plotwidget = fig[0, 0]
