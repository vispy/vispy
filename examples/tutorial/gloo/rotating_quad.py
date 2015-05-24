# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------

from vispy import gloo, app
from vispy.gloo import Program

vertex = """
    uniform float theta;
    attribute vec4 color;
    attribute vec2 position;
    varying vec4 v_color;
    void main()
    {
        float ct = cos(theta);
        float st = sin(theta);
        float x = 0.75* (position.x*ct - position.y*st);
        float y = 0.75* (position.x*st + position.y*ct);
        gl_Position = vec4(x, y, 0.0, 1.0);
        v_color = color;
    } """

fragment = """
    varying vec4 v_color;
    void main()
    {
        gl_FragColor = v_color;
    } """


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512), title='Rotating quad',
                            keys='interactive')
        self.timer = app.Timer('auto', self.on_timer)

        # Build program & data
        self.program = Program(vertex, fragment, count=4)
        self.program['color'] = [(1, 0, 0, 1), (0, 1, 0, 1),
                                 (0, 0, 1, 1), (1, 1, 0, 1)]
        self.program['position'] = [(-1, -1), (-1, +1),
                                    (+1, -1), (+1, +1)]
        self.program['theta'] = 0.0

        gloo.set_viewport(0, 0, *self.physical_size)

        self.clock = 0
        self.timer.start()

        self.show()

    def on_draw(self, event):
        gloo.set_clear_color('white')
        gloo.clear(color=True)
        self.program.draw('triangle_strip')

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_timer(self, event):
        self.clock += 0.001 * 1000.0 / 60.
        self.program['theta'] = self.clock
        self.update()

if __name__ == '__main__':
    c = Canvas()
    app.run()
