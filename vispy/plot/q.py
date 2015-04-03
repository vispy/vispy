# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ._fig import Fig
from ._plotwidget import _quick_method_list

__all__ = []

_figs = []

# XXX todo: pull docstring


def create_quick_plotter(method):
    """Helper to create quick plotters"""
    def fun(*args, **kwargs):
        fig = Fig()
        getattr(fig[0, 0], method)(*args, **kwargs)
        _figs.append(fig)
        return fig
    return fun


# create quick plotters
for method in _quick_method_list:
    fun = create_quick_plotter(method)
    globals()[method] = fun
    __all__.append(method)
