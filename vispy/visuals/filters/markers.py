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

    def _update_id_colors(self):
        """Update the ID colors buffer with appropriate divisor for rendering method."""
        # Call parent implementation to update colors
        super()._update_id_colors()

        # Set divisor=1 for instanced rendering so each marker gets its own ID
        if hasattr(self._visual, '_method') and self._visual._method == 'instanced':
            self._id_colors.divisor = 1
        else:
            self._id_colors.divisor = None
