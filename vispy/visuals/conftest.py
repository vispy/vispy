import pytest
from vispy.gloo.gl import use_gl


@pytest.fixture(params=['points', 'instanced'])
def rendering_method(request):
    """Setup rendering method for test function, skip if backend unavailable.

    Tests that accept this fixture will run twice: once with 'points' method
    (gl2) and once with 'instanced' method (gl+).
    """
    method = request.param

    if method == 'instanced':
        try:
            use_gl('gl+')
        except Exception:
            pytest.skip("gl+ backend not available for instanced rendering")
    else:
        use_gl('gl2')

    yield method

    # Reset to gl2 after test
    use_gl('gl2')
