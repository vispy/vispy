
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

        # Get positions of ticks and labels
        tick_fractions, tick_labels = self._get_tick_frac_labels()
        tick_pos, tick_label_pos = self._get_tick_positions(tick_fractions)

        # Initialize two LineVisuals - one for ticks, one for
        v_line = LineVisual(pos=self.extents, color=self.axis_color,
                          method='gl', width=3.0)

        v_ticks = LineVisual(pos=tick_pos, color=self.tick_color, method='gl',
                           width=2.0, connect='segments')

        v_text = TextVisual(list(tick_labels), pos=tick_label_pos, font_size=8,
                            color='w')

        v_line.draw(transforms)
        v_ticks.draw(transforms)
        v_text.draw(transforms)

    def _get_tick_direction(self):
        """Determines the tick direction if not specified."""
        v = self.vec

        if abs(v[0]) >= abs(v[1]): # rightward axis, rotate ticks clockwise
            v = np.dot(np.array([[0, -1], [1, 0]]), v)
        else: # upwards axis, rotate ticks counter-clockwise
            v = np.dot(np.array([[0, 1], [-1, 0]]), v)

        # now return a unit vector
        return v / np.linalg.norm(v)

    def _get_tick_positions(self, tick_fractions):
        tick_length = 10 # length in pixels

        tick_vector = self.tick_direction * tick_length

        tick_origins = np.tile(self.vec, (len(tick_fractions), 1))
        tick_origins = (self.extents[0].T + (tick_origins.T*tick_fractions).T)

        tick_endpoints = tick_vector + tick_origins

        tick_label_pos = tick_origins + self.tick_direction*30

        c = np.empty([len(tick_fractions) * 2, 2])
        c[0::2] = tick_origins
        c[1::2] = tick_endpoints

        return c, tick_label_pos

    def _get_tick_frac_labels(self):
        tick_num = 11 # number of ticks

        tick_fractions = np.linspace(0, 1, num=tick_num)
        tick_labels = str(tick_fractions)

        return tick_fractions, tick_labels
