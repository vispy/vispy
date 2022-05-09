# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_allclose

from vispy.scene.visuals import Text
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_text():
    """Test basic text support"""
    with TestingCanvas(bgcolor='w', size=(92, 92), dpi=92) as c:
        pos = [92 // 2] * 2
        text = Text('testing', font_size=20, color='k',
                    pos=pos, anchor_x='center', anchor_y='baseline',
                    parent=c.scene)
        # Test image created in Illustrator CS5, 1"x1" output @ 92 DPI
        assert_image_approved(c.render(), 'visuals/text1.png')

        text.text = ['foo', 'bar']
        text.pos = [10, 10]  # should auto-replicate
        text.rotation = [180, 270]
        try:
            text.pos = [10]
        except Exception:
            pass
        else:
            raise AssertionError('Exception not raised')
        c.update()
        c.app.process_events()
        text.pos = [[10, 10], [10, 20]]
        text.text = 'foobar'
        c.update()
        c.app.process_events()


@requires_application()
def test_text_rotation_update():

    # Regression test for a bug that caused text labels to not be redrawn
    # if the rotation angle was updated

    with TestingCanvas() as c:
        text = Text('testing', pos=(100, 100), parent=c.scene)
        c.update()
        c.app.process_events()
        assert_allclose(text.shared_program['a_rotation'], 0.)
        text.rotation = 30.
        c.update()
        c.app.process_events()
        assert_allclose(text.shared_program['a_rotation'], np.radians(30.))


@requires_application()
def test_face_bold_italic():

    with TestingCanvas() as c:

        # Check defaults
        text = Text('testing', pos=(100, 100), parent=c.scene)
        assert not text.bold and not text.italic

        # Check getter properties
        text = Text('testing', pos=(100, 100), bold=True, italic=True, parent=c.scene)
        assert text.bold and text.italic

        # Check that changing a property changes the font object
        font1 = text._font
        text.bold = False
        font2 = text._font
        assert font1 is not font2
        text.italic = False
        font3 = text._font
        assert font2 is not font3
        text.bold = True
        text.italic = True
        font4 = text._font
        assert font1 is font4


def test_text_depth_test():
    t = Text(depth_test=False)
    assert not t._vshare.gl_state["depth_test"]

    t = Text(depth_test=True)
    assert t._vshare.gl_state["depth_test"]

    t = Text()  # Default is false
    assert not t._vshare.gl_state["depth_test"]


run_tests_if_main()
