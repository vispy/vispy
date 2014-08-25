"""
The vispy.scene.visuals namespace provides a wide range of visuals.
A Visual is an Entity that displays something.

Visuals do not have to be used in a scenegraph per se; they can also
be used stand-alone e.g. from a vispy.app.Canvas, or using Glut.
"""

from .visual import Visual  # noqa
from .line import Line  # noqa
from .markers import Markers, marker_types  # noqa
from .mesh import Mesh  # noqa
from .image import Image  # noqa
from .polygon import Polygon  # noqa
from .ellipse import Ellipse  # noqa
from .regular_polygon import RegularPolygon  # noqa
from .rectangle import Rectangle  # noqa
from .text import Text  # noqa
from .grid_lines import GridLines  # noqa
from .surface_plot import SurfacePlot  # noqa
from .xyz_axis import XYZAxis  # noqa
from .plot_line import PlotLine  # noqa
