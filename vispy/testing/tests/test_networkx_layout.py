#format pep8
from vispy import testing
from vispy.visuals.graph.layouts import get_layout
import numpy as np

# conditional import
try:
    import networkx as nx
except:
    nx = None


def test_networkx_layout():
    """
    Testing the various inputs to the networkx layout
    """

    layout = get_layout("networkx_layout")

    graph = None
    if nx:
        # define graph
        graph = nx.complete_graph(5)
        # define positions
        pos = np.random.rand(5, 2)

        # test numpy array input
        testing.assert_true(
            isinstance(layout(graph, layout=positions), layout))

        # testing string input
        testing.assert_true(
            isinstance(layout(graph, layout="circular"), layout))

        # testing dict input
        pos = nx.circular_layout(graph)
        testing.assert_true(isinstance(layout(graph, pos), layout))

    else:
        # testing no graph
        testing.assert_raises(ValueError, layout(graph, positions))
    # testing wrong input
    testing.assert_raises(ValueError, layout([], []))
