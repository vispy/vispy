"""
A collection of cameras. Note that one can always overload
vispy.scene.Camera to create a custom camera.
"""

from __future__ import division

from .cams2d import NDCCamera, PixelCamera, TwoDCamera  # noqa
from .cams3d import ThreeDCamera, FirstPersonCamera  # noqa
