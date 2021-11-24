# -*- coding: utf-8 -*- 
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy.visuals.mesh import MeshVisual
from vispy.visuals.filters import WireframeFilter


def test_empty_mesh_wireframe():
    """Test that an empty mesh does not cause issues with wireframe filter"""
    mesh = MeshVisual()
    wf = WireframeFilter()
    mesh.attach(wf)

    # trigger update of filter
    wf.enabled = True
