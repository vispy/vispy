"""
The vispy.scene.visuals namespace provides a wide range of visuals.
A Visual is an Entity that displays something.

Visuals do not have to be used in a scenegraph per se; they can also
be used stand-alone e.g. from a vispy.app.Canvas, or using Glut.
"""

from .visual import Visual
from .line import Line
from .point import Point
from .image import Image
from .mesh import Mesh
from .polygon import Polygon
from .ellipse import Ellipse
