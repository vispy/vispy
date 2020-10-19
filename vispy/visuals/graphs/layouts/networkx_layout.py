#!/usr/bin/env python3
from ..util import _straight_line_vertices, issparse
import numpy as np, importlib


class NetworkxCoordinates:
    def __init__(self, graph, layout = None, *args, **kwargs):
        self.graph = graph
        self.positions = np.zeros((len(graph), 2), dtype = np.float32)
        # default random positions
        if type(layout) is type(None):
            self.positions = np.random.rand(*self.positions.shape)

        # check for networkx
        elif isinstance(layout, str):
            if USE_NETWORKX := importlib.util.find_spec("networkx"):
                import networkx as nx
                layout += "_layout" # append for nx
                if f := getattr(nx, layout):
                    self.positions = np.asarray([i for i in dict(f(graph, **kwargs)).values()])
                else:
                    raise ValueError("Check networkx for layouts")
            else:
                raise ValueError("networkx not found")
        # assume dict from networkx; values are 2-array
        elif isinstance(layout, dict):
            self.positions = np.asarray([i for i in layout.values()])

        # assume given values
        elif isinstance(layout, np.ndarray):
            assert layout.ndim == 2
            assert layout.shape[0] == len(graph)
            self.positions = layout
        else:
            raise ValueError("Input not understood")

        # normalize coordinates
        self.positions = (self.positions - self.positions.min()) / (self.positions.max() - self.positions.min())
        self.positions = self.positions.astype(np.float32)

    def __call__(self, adjacency_mat, directed = False):
        if issparse(adjacency_mat):
            adjacency_mat = adjacency_mat.tocoo()
        line_vertices, arrows = _straight_line_vertices(adjacency_mat, self.positions, directed)

        yield self.positions, line_vertices, arrows

    @property
    def adj(self):
        return nx.adjacency_matrix(self.graph)
