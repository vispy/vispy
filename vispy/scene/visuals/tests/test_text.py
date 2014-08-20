# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from vispy.app import Canvas
from vispy.scene.visuals import Text
from vispy import gloo
from vispy.testing import requires_application


@requires_application()
def test_text():
    """Test basic text support"""
    with Canvas(size=(100, 100)) as c:
        text = Text('X', bold=True, font_size=30, color='w')
        gloo.set_viewport(0, 0, *c.size)
        gloo.clear(color=(0., 0., 0., 1.))
        text.draw()

        s = gloo.util._screenshot()
        assert_equal(s.min(), 0)
        assert_equal(s.max(), 255)

        # let's just peek at the texture, make sure it has something
        gloo.clear(color=(0., 0., 0., 1.))
        gloo.util.draw_texture(text._font._atlas)
        s = gloo.util._screenshot()
        assert_equal(s.max(), 255)
        assert_equal(s.min(), 0)

if __name__ == '__main__':
    test_text()
