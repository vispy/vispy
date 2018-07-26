#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 20
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier, Guillaume Bâty. All Rights Reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
# High frequency (below pixel resolution) function plot
#
#  -> http://blog.hvidtfeldts.net/index.php/2011/07/plotting-high-frequency-fun
#     ctions-using-a-gpu/
#  -> https://www.shadertoy.com/view/4sB3zz
# -----------------------------------------------------------------------------
from vispy import gloo, app, keys

VERT_SHADER = """
attribute vec2 a_position;
void main (void)
{
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

FRAG_SHADER = """
uniform vec2 u_resolution;
uniform float u_global_time;

// --- Your function here ---
float function( float x )
{
    float d = 3.0 - 2.0*(1.0+cos(u_global_time/5.0))/2.0;
    return sin(pow(x,d))*sin(x);
}
// --- Your function here ---


float sample(vec2 uv)
{
    const int samples = 128;
    const float fsamples = float(samples);
    vec2 maxdist = vec2(0.5,1.0)/40.0;
    vec2 halfmaxdist = vec2(0.5) * maxdist;

    float stepsize = maxdist.x / fsamples;
    float initial_offset_x = -0.5 * fsamples * stepsize;
    uv.x += initial_offset_x;
    float hit = 0.0;
    for( int i=0; i<samples; ++i )
    {
        float x = uv.x + stepsize * float(i);
        float y = uv.y;
        float fx = function(x);
        float dist = abs(y-fx);
        hit += step(dist, halfmaxdist.y);
    }
    const float arbitraryFactor = 4.5;
    const float arbitraryExp = 0.95;
    return arbitraryFactor * pow( hit / fsamples, arbitraryExp );
}

void main(void)
{
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    float ymin = -2.0;
    float ymax = +2.0;
    float xmin = 0.0;
    float xmax = xmin + (ymax-ymin)* u_resolution.x / u_resolution.y;

    vec2 xy = vec2(xmin,ymin) + uv*vec2(xmax-xmin, ymax-ymin);
    gl_FragColor = vec4(0.0,0.0,0.0, sample(xy));
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys='interactive')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program["u_global_time"] = 0
        self.program['a_position'] = [(-1, -1), (-1, +1),
                                      (+1, -1), (+1, +1)]

        self.apply_zoom()

        gloo.set_state(blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self._timer = app.Timer('auto', connect=self.on_timer_event,
                                start=True)

        self.show()

    def on_resize(self, event):
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear('white')
        self.program.draw(mode='triangle_strip')

    def on_timer_event(self, event):
        if self._timer.running:
            self.program["u_global_time"] += event.dt
        self.update()

    def on_key_press(self, event):
        if event.key is keys.SPACE:
            if self._timer.running:
                self._timer.stop()
            else:
                self._timer.start()

    def apply_zoom(self):
        self.program["u_resolution"] = self.physical_size
        gloo.set_viewport(0, 0, *self.physical_size)


if __name__ == '__main__':
    c = Canvas()
    app.run()
