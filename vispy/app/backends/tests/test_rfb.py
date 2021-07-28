# This currenly only tests that the backend exists and can be imported ...

def test_rfb():
    from vispy.app.backends import _jupyter_rfb
    _jupyter_rfb  # flake
