# -*- coding: utf-8 -*-
from vispy.scene.visuals import Text
from vispy.testing import (requires_application, TestingCanvas,
                           assert_image_equal, run_tests_if_main)


@requires_application()
def test_text():
    """Test basic text support"""
    
    with TestingCanvas(bgcolor='w', size=(92, 92)) as c:
        #c.context.glir.clear()  # Just to be safe
        pos = [92 // 2] * 2
        text = Text('testing', font_size=20, color='k',
                    pos=pos, anchor_x='center', anchor_y='baseline')
        c.draw_visual(text)
        # This limit seems large, but the images actually match quite well...
        # TODO: we should probably make more "modes" for assert_image_equal
        # at some point
        # Test image created in Illustrator CS5, 1"x1" output @ 92 DPI
        assert_image_equal("screenshot", 'visuals/text1.png', limit=840)


run_tests_if_main()
