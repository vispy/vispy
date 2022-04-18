# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy.scene.widgets import ViewBox
from vispy.testing import run_tests_if_main


def test_turntable_camera_link():
    vbs = [ViewBox(camera='turntable') for _ in range(3)]
    cams = [vb.camera for vb in vbs]

    for cam in cams:
        cam.elevation = 45.0
        cam.azimuth = 120.0
        cam.scale_factor = 4.0

    cams[0].link(cams[1])
    cams[0].link(cams[2], props=['azimuth', 'elevation'])

    cams[1].elevation = 30.0
    cams[1].azimuth = 90.0
    cams[1].scale_factor = 2.0

    assert cams[0].elevation == 30.0
    assert cams[0].azimuth == 90.0
    assert cams[0].scale_factor == 2.0

    assert cams[2].elevation == 30.0
    assert cams[2].azimuth == 90.0
    assert cams[2].scale_factor == 4.0


def test_panzoom_link():
    vbs = [ViewBox(camera='panzoom') for _ in range(4)]
    cams = [vb.camera for vb in vbs]

    for cam in cams:
        cam.rect = (0, 0, 100, 100)

    cams[0].link(cams[1])
    cams[0].link(cams[2], axis='x')
    cams[0].link(cams[3], axis='y')

    cams[1].rect = (-20, -20, 130, 130)

    assert cams[0].rect.pos == (-20, -20) and cams[0].rect.size == (130, 130)
    assert cams[2].rect.pos == (-20, 0) and cams[2].rect.size == (130, 100)
    assert cams[3].rect.pos == (0, -20) and cams[3].rect.size == (100, 130)


run_tests_if_main()
