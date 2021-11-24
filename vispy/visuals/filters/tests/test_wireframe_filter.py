# -*- coding: utf-8 -*-

from vispy.visuals.mesh import Mesh
from vispy.visuals.filters import WireframeFilter


def test_empty_mesh_wireframe():
    """Test that an empty mesh does not cause issues with wireframe filter"""
    mesh = Mesh()
    wf = WireframeFilter()
    mesh.attach(wf)

    # trigger update of filter
    wf.enabled = True
