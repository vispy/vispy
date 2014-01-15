"""
A collection of cameras. Note that one can always overload
vispy.scene.Camera to create a custom camera.
"""

from __future__ import print_function, division, absolute_import

from .cams2d import NDCCamera, PixelCamera, TwoDCamera
from .cams3d import ThreeDCamera, FirstPersonCamera
