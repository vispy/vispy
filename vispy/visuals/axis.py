
import numpy as np

from .line import LineVisual
from .text import TextVisual

class AxisVisual(LineVisual):
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
                 scale_type="linear"):
        color = (1, 1, 1, 1)

        self.extents = extents
        self.vec = np.subtract(self.extents[1],self.extents[0])

        self.tick_direction = tick_direction or self._get_tick_direction()

        LineVisual.__init__(self, pos=extents, color=color, mode='gl',
                            width=3.0)

    def draw_ticks(self, transforms):
        t = TicksVisual(pos=self._get_tick_positions())
        t.draw(transforms)

        tt = TickTextVisual()

    def _get_tick_direction(self):
        """Determines the tick direction if not specified."""

        v = self.vec

        right = np.array([1, 0])
        up = np.array([0, -1])

        # This will be negative if the axis is pointing upwards,
        # and positive if right.
        rightness = np.linalg.norm(v*right)-np.linalg.norm(v*up)

        if np.sign(rightness) >= 0:
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


class TicksVisual(LineVisual):
    def __init__(self, pos, domain=(0., 1.)):
        color = (0.7, 0.7, 0.7, 1)

        LineVisual.__init__(self, pos=pos, color=color, mode='gl',
                            width=2.0, connect='segments')

class TickTextVisual(TextVisual):
    def __init__(self, **kwargs):
        pass
