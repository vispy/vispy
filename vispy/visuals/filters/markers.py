import numpy as np

from vispy.visuals.filters import PrimitivePickingFilter


class MarkerPickingFilter(PrimitivePickingFilter):
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

    def _update_id_colors(self):
        if self._visual._data is None:
            n_markers = 0
        else:
            n_markers = len(self._visual._data['a_position'])

        # we only care about the number of markers changing
        if self._n_primitives == n_markers:
            return
        self._n_primitives = n_markers

        # pack the marker ids into a color buffer
        ids = np.arange(1, n_markers + 1, dtype=np.uint32)
        id_colors = self._pack_ids_into_rgba(ids)
        self._id_colors.set_data(id_colors)
