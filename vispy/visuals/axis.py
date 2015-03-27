
import numpy as np

from .line import LineVisual
from .text import TextVisual

class AxisVisual(LineVisual):
    """
    Single axis.
    """
    def __init__(self, extents, domain=(0., 1.)):
        color = (1, 1, 1, 1)

        self.extents = extents

        LineVisual.__init__(self, pos=extents, color=color, mode='gl',
                            width=3.0)

    def draw_ticks(self, transforms):
        t = TicksVisual(extents=self.extents)
        t.draw(transforms)

class TicksVisual(LineVisual):
    def __init__(self, extents, domain=(0., 1.)):
        color = (0.7, 0.7, 0.7, 1)

        # Generate 10 evenly-spaced ticks
        tick_spaces = np.linspace(extents[0][0], extents[1][0], num=10)

        x = np.repeat(tick_spaces, 2)
        y = np.tile([extents[0][1], extents[0][1] + 10], len(tick_spaces))

        tickpos=np.c_[x,y]

        LineVisual.__init__(self, pos=tickpos, color=color, mode='gl',
                            width=2.0, connect='segments')

class TickTextVisual(TextVisual):
    def __init__(self, **kwargs):
        pass
