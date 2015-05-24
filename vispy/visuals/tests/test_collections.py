# *Very* basic collections tests

from vispy.visuals.collections import (PathCollection, PointCollection,
                                       PolygonCollection, SegmentCollection,
                                       TriangleCollection)
from vispy.testing import requires_application, TestingCanvas


@requires_application()
def test_init():
    """Test collection initialization
    """
    with TestingCanvas():
        for coll in (PathCollection, PointCollection, PolygonCollection,
                     SegmentCollection, TriangleCollection):
            coll()
