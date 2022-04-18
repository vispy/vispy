# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from .base_camera import BaseCamera
from .perspective import PerspectiveCamera
from .panzoom import PanZoomCamera
from .arcball import ArcballCamera
from .turntable import TurntableCamera
from .fly import FlyCamera


def make_camera(cam_type, *args, **kwargs):
    """Factory function for creating new cameras using a string name.

    Parameters
    ----------
    cam_type : str
        May be one of:

            * 'panzoom' : Creates :class:`PanZoomCamera`
            * 'turntable' : Creates :class:`TurntableCamera`
            * None : Creates :class:`Camera`

    Notes
    -----
    All extra arguments are passed to the __init__ method of the selected
    Camera class.
    """
    cam_types = {None: BaseCamera}
    for camType in (BaseCamera, PanZoomCamera, PerspectiveCamera,
                    TurntableCamera, FlyCamera, ArcballCamera):
        cam_types[camType.__name__[:-6].lower()] = camType

    try:
        return cam_types[cam_type](*args, **kwargs)
    except KeyError:
        raise KeyError('Unknown camera type "%s". Options are: %s' %
                       (cam_type, cam_types.keys()))
