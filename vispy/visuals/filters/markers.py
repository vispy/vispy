import numpy as np

from vispy.visuals.filters import PrimitivePickingFilter


class MarkerPickingFilter(PrimitivePickingFilter):
    """Filter used to color markers by a picking ID.

    Note that the ID color uses the alpha channel, so this may not be used
    with blending enabled.

    Examples
    --------
    :ref:`sphx_glr_gallery_scene_marker_picking.py`
    """

    def _get_picking_ids(self):
        if self._visual._data is None:
            n_markers = 0
        else:
            n_markers = len(self._visual._data['a_position'])

        # we only care about the number of markers changing
        if self._n_primitives == n_markers:
            return
        self._n_primitives = n_markers

        return np.arange(1, n_markers + 1, dtype=np.uint32)
