
import numpy as np

from .line import LineVisual
from .text import TextVisual

class AxisVisual(LineVisual):
    """
    Single axis.
    """
    def __init__(self, extents, domain=(0., 1.), range=(0., 1.)):
        color = np.array([[1, 1, 1, 1],
                          [1, 1, 1, 1]])

        LineVisual.__init__(self, pos=extents, color=color, mode='gl',
                            width=4.0)

class TicksVisual(LineVisual):
    def __init__(self, **kwargs):
        pass

class TickTextVisual(TextVisual):
    def __init__(self, **kwargs):
        pass
