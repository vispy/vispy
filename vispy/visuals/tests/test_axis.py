# -*- coding: utf-8 -*-

"""
Tests for AxisVisual
"""

from vispy import scene
from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


@requires_application()
def test_axis():
    with TestingCanvas() as c:
        axis = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]])
        c.draw_visual(axis)

@requires_application()
def test_axis_alt():

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    scene_transform = scene.STTransform()
    view.camera = scene.cameras.TurntableCamera(parent=view.scene,
                                                fov=0., distance=4.0)
    axes = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], parent=view.scene)
    canvas.render()


run_tests_if_main()
