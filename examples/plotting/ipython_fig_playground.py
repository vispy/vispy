#!/usr/bin/env ipython -i ipython_fig_playground.py
# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Boilerplate Interactive Plotting Session
========================================

Bare bones plotting region that can be used with the python
interpreter as a playground.

Run with:

.. code-block:: bash

    python -i ipython_fig_playground.py

"""
from vispy import plot as vp  # noqa
import numpy as np  # noqa

fig = vp.Fig(size=(600, 500))  # noqa
plotwidget = fig[0, 0]
