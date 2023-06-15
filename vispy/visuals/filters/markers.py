import numpy as np

from vispy.gloo import VertexBuffer
from vispy.visuals.shaders import Function
from vispy.visuals.filters import Filter


class MarkerPickingFilter(Filter):
    """Filter used to color markers by a picking ID.

    Note that the ID color uses the alpha channel, so this may not be used
    with blending enabled.

    Examples
    --------
    See
    `examples/scene/marker_picking.py
    <https://github.com/vispy/vispy/blob/main/examples/scene/marker_picking.py>`_
    example script.
    """

    def __init__(self):
        vfunc = Function("""\
            varying vec4 v_marker_picking_color;
            void prepare_marker_picking() {
                v_marker_picking_color = $ids;
            }
        """)
        ffunc = Function("""\
            varying vec4 v_marker_picking_color;
            void marker_picking_filter() {
                if ($enabled != 1) {
                    return;
                }
                gl_FragColor = v_marker_picking_color;
            }
        """)

        self._ids = VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        vfunc['ids'] = self._ids
        super().__init__(vcode=vfunc, fcode=ffunc)
        self._n_markers = 0
        self.enabled = False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, e):
        self._enabled = bool(e)
        self.fshader['enabled'] = int(self._enabled)
        self._update_data()

    def _update_data(self):
        if not self.attached:
            return

        if self._visual._data is None:
            n = 0
        else:
            n = len(self._visual._data['a_position'])

        # we only care about the number of markers changing
        if self._n_markers == n:
            return
        self._n_markers = n

        # pack the marker ids into a color buffer
        ids = np.arange(
            1, n + 1,
            dtype=np.uint32
        ).view(np.uint8).reshape(n, 4)
        ids = np.divide(ids, 255, dtype=np.float32)
        self._ids.set_data(ids)

    def on_data_updated(self, event):
        self._update_data()

    def _attach(self, visual):
        super()._attach(visual)
        visual.events.data_updated.connect(self.on_data_updated)
        self._update_data()

    def _detach(self, visual):
        visual.events.data_updated.disconnect(self.on_data_updated)
        super()._detach(visual)
