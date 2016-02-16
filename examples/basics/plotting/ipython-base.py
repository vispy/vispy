# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Bare bones plotting region that can be used with the python
interpreter as a playground.

Run with
python -i ipython-base.py
"""


import vispy
from vispy.plot import *


fig = Fig()
plotwidget = fig[0]
