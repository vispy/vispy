# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy import testing
from vispy.visuals.graphs.layouts import get_layout
from vispy.visuals.graphs.layouts.networkx_layout import NetworkxCoordinates
import numpy as np

# conditional import
try:
    import networkx as nx
except ModuleNotFoundError:
    nx = None


def test_networkx_layout_with_graph():
    """Testing the various inputs to the networkx layout."""
    settings = dict(name="networkx_layout")
    if nx is None:
        return testing.SkipTest("'networkx' required")

    # empty input
    # testing.assert_raises(ValueError("Requires networkx input"), get_layout(**settings))

    # define graph
    graph = nx.complete_graph(5)
    # define positions
    layout = np.random.rand(5, 2)
    settings['graph'] = graph
    settings['layout'] = layout

    # test numpy array input
    testing.assert_true(isinstance(
        get_layout(**settings), NetworkxCoordinates))
    # testing string input
    settings['layout'] = 'circular'
    testing.assert_true(isinstance(
        get_layout(**settings), NetworkxCoordinates))
    # testing dict input
    settings['layout'] = nx.circular_layout(graph)
    testing.assert_true(isinstance(
        get_layout(**settings), NetworkxCoordinates))


def test_networkx_layout_no_networkx():
    settings = dict(name="networkx_layout")
    testing.assert_raises(ValueError, get_layout, **settings)
