# -*- coding: utf-8 -*-
from vispy.scene.visuals import SurfacePlot 
from vispy.scene import TurntableCamera
from vispy.color import get_colormap
from vispy.testing import requires_application, TestingCanvas, run_tests_if_main
from vispy.testing.image_tester import assert_image_reasonable

import numpy as np
import pytest


@requires_application()
@pytest.mark.parametrize('x1dim', [True, False])
@pytest.mark.parametrize('y1dim', [True, False])
def test_surface_plot(x1dim:bool, y1dim:bool):
    """Test SurfacePlot visual"""
    with TestingCanvas(bgcolor='w') as c:
        
        # create data
        nx, ny = (100, 150)
        x = np.linspace(-2, 2, nx)
        y = np.linspace(-3, 3, ny)
        xv, yv = np.meshgrid(x, y, indexing="ij")
        z = np.sin(xv**2 + yv**2)

        view = c.central_widget.add_view()
        view.camera = TurntableCamera(up='z', fov=60)

        # color vertices
        cnorm = z / abs(np.amax(z))
        colormap = get_colormap("viridis").map(cnorm)
        colormap.reshape(z.shape + (-1,))

        # 1 or 2 dimensional x and y data
        x_input = x if x1dim else xv
        y_input = y if y1dim else yv

        # create figure
        surface = SurfacePlot(z=z,
                              x=x_input,
                              y=y_input,
                              shading=None)
        
        surface.mesh_data.set_vertex_colors(colormap)

        # c.draw_visual(surface) 
        view.add(surface)

        assert_image_reasonable(c.render())


run_tests_if_main()
