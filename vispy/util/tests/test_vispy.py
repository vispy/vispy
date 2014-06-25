""" Tests to ensure that base vispy namespace functions correctly,
including configuration options.
"""

import vispy
from vispy.testing import requires_application

@requires_application('pyside')
def test_use():
    vispy.use('')  # Should do nothing
    vispy.use('pyside')  # So this should always work
    vispy.use('desktop')
    vispy.use('pyside desktop')
