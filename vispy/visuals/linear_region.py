import numpy as np

from .. import gloo
from .visual import Visual


VERT_SHADER = """
    attribute vec2 a_pos;
    varying vec4 v_color;

    void main() {
        vec4 pos = vec4(a_pos, 0, 1);

        if($is_vertical==1)
        {
            pos.y = $render_to_visual(pos).y;
        }
        else
        {
            pos.x = $render_to_visual(pos).x;
        }

        gl_Position = $transform(pos);
        gl_PointSize = 10;
        v_color = $color;
    }
    """

FRAG_SHADER = """
    varying vec4 v_color;

    void main() {
        gl_FragColor = v_color;
    }
    """


class LinearRegionVisual(Visual):
    """Infinite horizontal or vertical region for 2D plots.

    Parameters
    ----------
    pos : list, tuple or numpy array
        Bounds of the region along the axis. len(bounds) must be 2.
    color : list, tuple, or array
        The color to use when drawing the line. If an array is given, it
        must be of shape (1, 4) and provide one rgba color.
    vertical:
        True for drawing a vertical region, False for an horizontal region
    """

    def __init__(self, pos=None, color=(1.0, 1.0, 1.0, 1.0), vertical=True):
        """

        """
        Visual.__init__(self, vcode=VERT_SHADER, fcode=FRAG_SHADER)

        self._changed = {'pos': False, 'color': False}

        self.pos_buf = gloo.VertexBuffer()
        # The Visual superclass contains a MultiProgram, which is an object
        # that behaves like a normal shader program (you can assign shader
        # code, upload values, set template variables, etc.) but internally
        # manages multiple ModularProgram instances, one per view.

        # The MultiProgram is accessed via the `shared_program` property, so
        # the following modifications to the program will be applied to all
        # views:
        self.shared_program['a_pos'] = self.pos_buf
        self._program.vert['is_vertical'] = 1 if vertical else 0

        self._need_upload = False
        self._is_vertical = bool(vertical)
        self._pos = np.zeros((4, 2), dtype=np.float32)

        # Visual keeps track of draw mode, index buffer, and GL state. These
        # are shared between all views.
        self._draw_mode = 'triangle_strip'
        self.set_gl_state('translucent', depth_test=False)

        self.set_data(pos=pos, color=color)

    def set_data(self, pos=None, color=None):
        if pos is not None:

            b0 = min(pos)
            b1 = max(pos)
            if self._is_vertical:
                self._pos = np.array([[b1, 1], [b0, 1],
                                      [b1, -1], [b0, -1]],
                                     dtype=np.float32)
            else:
                self._pos = np.array([[1, b1], [1, b0],
                                      [-1, b1], [-1, b0]],
                                     dtype=np.float32)
            self._changed['pos'] = True

        if color is not None:
            if type(color) not in [tuple, list, np.ndarray] \
               or len(color) != 4:
                raise ValueError('color must be a float rgba tuple, '
                                 'list or array')
            self._color = np.ascontiguousarray(list(color), dtype=np.float32)
            self._changed['color'] = True

    @property
    def color(self):
        return self._color

    @property
    def pos(self):
        pos = self._pos
        if self._is_vertical:
            return (pos[1, 0], pos[0, 0])
        else:
            return (pos[1, 1], pos[0, 1])

    def _compute_bounds(self, axis, view):
        """Return the (min, max) bounding values of this visual along *axis*
        in the local coordinate system.
        """
        is_vertical = self._is_vertical
        pos = self._pos
        if axis == 0 and is_vertical:
            return (pos[1, 0], pos[0, 0])
        elif axis == 1 and not is_vertical:
            return (pos[1, 1], pos[0, 1])

        return None

    @property
    def is_vertical(self):
        return self._is_vertical

    def _prepare_transforms(self, view=None):
        program = view.view_program
        transforms = view.transforms
        program.vert['render_to_visual'] = transforms.get_transform('render',
                                                                    'visual')
        program.vert['transform'] = transforms.get_transform('visual',
                                                             'render')

    def _prepare_draw(self, view=None):
        """This method is called immediately before each draw.

        The *view* argument indicates which view is about to be drawn.
        """

        if self._changed['pos']:
            self.pos_buf.set_data(self._pos)
            self._changed['pos'] = False

        if self._changed['color']:
            self._program.vert['color'] = self._color
            self._changed['color'] = False

        return True
