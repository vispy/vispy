# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy import scene, io
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_perspective_render():
    with TestingCanvas(size=(120, 200)) as canvas:

        grid = canvas.central_widget.add_grid()
        grid.padding = 20

        imdata = io.load_crate().astype('float32') / 255

        views = []
        images = []
        for i, imethod in enumerate(['impostor', 'subdivide']):
            v = grid.add_view(row=i, col=0, border_color='white')
            v.camera = 'turntable'
            v.camera.fov = 50
            v.camera.distance = 30

            views.append(v)
            image = scene.visuals.Image(imdata, method=imethod,
                                        grid=(4, 4))
            image.transform = scene.STTransform(translate=(-12.8, -12.8),
                                                scale=(0.1, 0.1))
            v.add(image)
            images.append(image)

        image = canvas.render()
        canvas.close()

        # Allow many pixels to differ by a small amount--texture sampling and
        # exact triangle position will differ across platforms. However a
        # change in perspective or in the widget borders should trigger a
        # failure.
        assert_image_approved(image, 'scene/cameras/perspective_test.png',
                              'perspective test 1: 2 identical views with '
                              'correct perspective',
                              px_threshold=20,
                              px_count=60,
                              max_px_diff=200)


run_tests_if_main()
