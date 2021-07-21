# This currenly only tests that the backend exists and can be imported ...

def test_rfb():
    from vispy.app.backends import _ipynb_rfb
    _ipynb_rfb  # flake
