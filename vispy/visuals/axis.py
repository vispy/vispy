
import numpy as np

from .visual import Visual
from .line import LineVisual
from .text import TextVisual

class AxisVisual(Visual):
    """Axis visual

    Parameters
    ----------
    extents : array
        Co-ordinates of start and end of the axis.
    tick_direction : array
        Unit vector specifying the direction of the ticks. Default is
        left/down. (This will be normalised to a unit vector)
    domain : tuple
        The data values at the beginning and end of the axis, used for tick
        labels. i.e. (5, 10) means the axis starts at 5 and ends at 10.
    scale_type : str
        The type of scale. Default is 'linear'. Options:
            * "linear"
            * "logarithmic"
            * "power"
    """
    def __init__(self, extents, tick_direction = None, domain=(0., 1.),
                 scale_type="linear", axis_color=(1, 1, 1, 1),
                 tick_color = (0.7, 0.7, 0.7, 1)):
        self.axis_color = axis_color
        self.tick_color = tick_color

        self.extents = extents
        self.vec = np.subtract(self.extents[1],self.extents[0])

        self.tick_direction = tick_direction or self._get_tick_direction()

    def draw(self, transforms):
        line = LineVisual(pos=self.extents, color=self.axis_color,
                          mode='gl', width=3.0)

        ticks = LineVisual(pos=self._get_tick_positions(),
                           color=self.tick_color, mode='gl',
                           width=2.0, connect='segments')

        ticks.draw(transforms)
        line.draw(transforms)

    def _get_tick_direction(self):
        """Determines the tick direction if not specified."""
        v = self.vec

        if abs(v[0]) >= abs(v[1]):
            v = np.dot(np.array([[0, -1], [1, 0]]), v) # right axis, down ticks
        else:
            v = np.dot(np.array([[0, 1], [-1, 0]]), v) # up axis, left ticks

        # now return a unit vector
        return v / np.linalg.norm(v)

    def _get_tick_positions(self):
        tick_num = 10 # number of ticks
        tick_length = 10 # length in pixels

        tick_vector = self.tick_direction * tick_length

        tick_fractions = np.linspace(0, 1, num=tick_num)

        tick_origins = np.tile(self.vec, (len(tick_fractions), 1))
        tick_origins = (self.extents[0].T + (tick_origins.T*tick_fractions).T)

        tick_endpoints = tick_vector + tick_origins

        c = np.empty([tick_num * 2, 2])
        c[0::2] = tick_origins
        c[1::2] = tick_endpoints

        return c
