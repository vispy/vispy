
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

        self.tick_direction = tick_direction or self._get_tick_direction()

        LineVisual.__init__(self, pos=extents, color=color, mode='gl',
                            width=3.0)

    def draw_ticks(self, transforms):
        t = TicksVisual(pos=self._get_tick_positions())
        t.draw(transforms)

        tt = TickTextVisual()

    def _get_tick_direction(self):
        """Determines the tick direction if not specified."""

        right = np.array([1, 0])
        up = np.array([0, -1])

        a = np.subtract(self.extents[1],self.extents[0])

        # This will be negative if the axis is pointing upwards,
        # and positive if right.
        rightness = np.linalg.norm(a*right)-np.linalg.norm(a*up)

        if np.sign(rightness) >= 0:
            a = np.dot(np.array([[0, -1], [1, 0]]), a) # right axis, down ticks
        else:
            a = np.dot(np.array([[0, 1], [-1, 0]]), a) # up axis, left ticks

        # now return a unit vector
        return a / np.linalg.norm(a)

    def _get_tick_positions(self):
        # Generate 10 evenly-spaced ticks
        tick_spaces = np.linspace(self.extents[0][0],
                                  self.extents[1][0], num=10)

        x = np.repeat(tick_spaces, 2)
        y = np.tile([self.extents[0][1],
                    self.extents[0][1] + 10], len(tick_spaces))

        return np.c_[x,y]


class TicksVisual(LineVisual):
    def __init__(self, pos, domain=(0., 1.)):
        color = (0.7, 0.7, 0.7, 1)

        LineVisual.__init__(self, pos=pos, color=color, mode='gl',
                            width=2.0, connect='segments')

class TickTextVisual(TextVisual):
    def __init__(self, **kwargs):
        pass
