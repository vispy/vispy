# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.color import Color
from vispy.geometry import create_cube, create_sphere
from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl)
from vispy.visuals.filters import ShadingFilter, WireframeFilter
from vispy.visuals.filters.mesh import _as_rgba

import pytest


@requires_pyopengl()
def test_mesh_color():
    # Create visual
    vertices, filled_indices, outline_indices = create_cube()
    axis = scene.visuals.Mesh(vertices['position'], outline_indices,
                              color='black', mode='lines')

    # Change color (regression test for a bug that caused this to reset
    # the vertex data to None)

    axis.color = (0.1, 0.3, 0.7, 0.9)

    new_vertices = axis.mesh_data.get_vertices()

    np.testing.assert_allclose(axis.color.rgba, (0.1, 0.3, 0.7, 0.9))
    np.testing.assert_allclose(vertices['position'], new_vertices)


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('shading', [None, 'flat', 'smooth'])
def test_mesh_shading_change_from_none(shading):
    # Regression test for #2041: exception raised when changing the shading
    # mode with shading=None initially.
    size = (45, 40)
    with TestingCanvas(size=size) as c:
        v = c.central_widget.add_view(border_width=0)
        vertices = np.array([(0, 0, 0), (0, 0, 1), (1, 0, 0)], dtype=float)
        faces = np.array([(0, 1, 2)])
        mesh = scene.visuals.Mesh(vertices=vertices, faces=faces, shading=None)
        v.add(mesh)
        c.render()
        # This below should not fail.
        mesh.shading = shading
        c.render()


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('shading', [None, 'flat', 'smooth'])
def test_mesh_shading_filter(shading):
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        mdata = create_sphere(20, 30, radius=1)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=shading,
                                  color=(0.2, 0.3, 0.7, 1.0))
        v.add(mesh)

        rendered = c.render()[..., 0]  # R channel only
        if shading in ("flat", "smooth"):
            # there should be a gradient, not solid colors
            assert np.unique(rendered).size >= 28
            # sphere/circle is "dark" on the right and gets brighter as you
            # move to the left, then hits a bright spot and decreases after
            invest_row = rendered[34].astype(np.float64)
            # overall, we should be increasing brightness up to a "bright spot"
            assert (np.diff(invest_row[34:60]) <= 0).all()
        else:
            assert np.unique(rendered).size == 2


def test_intensity_or_color_as_rgba():
    assert _as_rgba(0.3) == Color((1.0, 1.0, 1.0, 0.3))
    assert _as_rgba((0.3, 0.2, 0.1)) == Color((0.3, 0.2, 0.1, 1.0))
    assert _as_rgba((0.3, 0.2, 0.1, 0.5)) == Color((0.3, 0.2, 0.1, 0.5))


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('shading', [None, 'flat', 'smooth'])
def test_mesh_shading_filter_enabled(shading):
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        mdata = create_sphere(20, 30, radius=1)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=None,
                                  color=(0.2, 0.3, 0.7, 1.0))
        shading_filter = ShadingFilter(shading=shading)
        mesh.attach(shading_filter)
        v.add(mesh)

        shading_filter.enabled = False
        rendered_without_shading = c.render()

        shading_filter.enabled = True
        rendered_with_shading = c.render()

        if shading is None:
            # There should be no shading applied, regardless of the value of
            # `enabled`.
            assert np.allclose(rendered_without_shading, rendered_with_shading)
        else:
            # The result should be different with shading applied.
            assert not np.allclose(rendered_without_shading,
                                   rendered_with_shading)


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('attribute', ['ambient_coefficient',
                                       'diffuse_coefficient',
                                       'specular_coefficient',
                                       'ambient_light',
                                       'diffuse_light',
                                       'specular_light'])
def test_mesh_shading_filter_colors(attribute):
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        base_color_white = (1.0, 1.0, 1.0, 1.0)
        overlay_color_red = (1.0, 0.0, 0.0, 1.0)

        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        mdata = create_sphere(20, 30, radius=1)
        mesh = scene.visuals.Mesh(meshdata=mdata, color=base_color_white)
        v.add(mesh)

        shading_filter = ShadingFilter(shading='smooth',
                                       # Set the light source on the side of
                                       # and around the camera to get a clearly
                                       # visible reflection.
                                       light_dir=(-5, -5, 5),
                                       # Activate all illumination types as
                                       # white light but reduce the intensity
                                       # to prevent saturation.
                                       ambient_light=0.3,
                                       diffuse_light=0.3,
                                       specular_light=0.3,
                                       # Get a wide highlight.
                                       shininess=4)
        mesh.attach(shading_filter)

        rendered_white = c.render()

        setattr(shading_filter, attribute, overlay_color_red)
        rendered_red = c.render()

        # The results should be different.
        assert not np.allclose(rendered_white, rendered_red)

        # There should be an equal amount of all colors in the white rendering.
        color_count_white = rendered_white.sum(axis=(0, 1))
        r, g, b, _ = color_count_white
        assert r == g and r == b

        color_count_red = rendered_red.sum(axis=(0, 1))
        # There should be more red in the red-colored rendering.
        r, g, b, _ = color_count_red
        assert r > g and r > b


@requires_pyopengl()
def test_mesh_bounds():
    # Create 3D visual
    vertices, filled_indices, outline_indices = create_cube()
    axis = scene.visuals.Mesh(vertices['position'], outline_indices,
                              color='black', mode='lines')

    # Test bounds for all 3 axes
    for i in range(3):
        np.testing.assert_allclose(axis.bounds(i), (-1.0, 1.0))

    # Create 2D visual using projection of cube
    axis = scene.visuals.Mesh(vertices['position'][:, :2], outline_indices,
                              color='black', mode='lines')

    # Test bounds for first 2 axes
    for i in range(2):
        np.testing.assert_allclose(axis.bounds(i), (-1.0, 1.0))
    # Test bounds for 3rd axis
    np.testing.assert_allclose(axis.bounds(2), (0.0, 0.0))


@requires_pyopengl()
@requires_application()
def test_mesh_wireframe_filter():
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        # Create visual
        mdata = create_sphere(20, 40, radius=20)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=None,
                                  color=(0.1, 0.3, 0.7, 0.9))
        wireframe_filter = WireframeFilter(color='red')
        mesh.attach(wireframe_filter)
        v.add(mesh)
        from vispy.visuals.transforms import STTransform
        mesh.transform = STTransform(translate=(20, 20))
        mesh.transforms.scene_transform = STTransform(scale=(1, 1, 0.01))

        rendered_with_wf = c.render()
        assert np.unique(rendered_with_wf[..., 0]).size >= 50

        wireframe_filter.enabled = False
        rendered_wo_wf = c.render()
        # the result should be completely different
        # assert not allclose
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf, rendered_wo_wf)

        wireframe_filter.enabled = True
        wireframe_filter.wireframe_only = True
        rendered_with_wf_only = c.render()
        # the result should be different from the two cases above
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf_only, rendered_with_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf_only, rendered_wo_wf)

        wireframe_filter.enabled = True
        wireframe_filter.wireframe_only = False
        wireframe_filter.faces_only = True
        rendered_with_faces_only = c.render()
        # the result should be different from the cases above
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_with_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_wo_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_with_wf_only)


run_tests_if_main()
