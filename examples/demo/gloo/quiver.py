#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------

from vispy import app, gloo

vertex = """
attribute vec2 position;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment = """

vec4 stroke(float distance, float linewidth, float antialias, vec4 stroke)
{
    vec4 frag_color;
    float t = linewidth/2.0 - antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/antialias;
    alpha = exp(-alpha*alpha);
    if( border_distance > (linewidth/2.0 + antialias) )
        discard;
    else if( border_distance < 0.0 )
        frag_color = stroke;
    else
        frag_color = vec4(stroke.rgb, stroke.a * alpha);
    return frag_color;
}

vec4 filled(float distance, float linewidth, float antialias, vec4 fill)
{
    vec4 frag_color;
    float t = linewidth/2.0 - antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/antialias;
    alpha = exp(-alpha*alpha);
    // Within linestroke
    if( border_distance < 0.0 )
        frag_color = fill;
    // Within shape
    else if( signed_distance < 0.0 )
        frag_color = fill;
    else
        // Outside shape
        if( border_distance > (linewidth/2.0 + antialias) )
            discard;
        else // Line stroke exterior border
            frag_color = vec4(fill.rgb, alpha * fill.a);
    return frag_color;
}

// Computes the signed distance from a line
float line_distance(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    return dot(rel_p, vec2(dir.y, -dir.x));
}

// Computes the signed distance from a line segment
float segment_distance(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    float dist1 = abs(dot(rel_p, vec2(dir.y, -dir.x)));
    float dist2 = abs(dot(rel_p, dir)) - 0.5*len;
    return max(dist1, dist2);
}

// Computes the center with given radius passing through p1 & p2
vec4 circle_from_2_points(vec2 p1, vec2 p2, float radius)
{
    float q = length(p2-p1);
    vec2 m = (p1+p2)/2.0;
    vec2 d = vec2( sqrt(radius*radius - (q*q/4.0)) * (p1.y-p2.y)/q,
                   sqrt(radius*radius - (q*q/4.0)) * (p2.x-p1.x)/q);
    return  vec4(m+d, m-d);
}

float arrow_curved(vec2 texcoord,
                   float body, float head,
                   float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    float height = 0.5;
    vec2 p1 = end - head*vec2(+1.0,+height);
    vec2 p2 = end - head*vec2(+1.0,-height);
    vec2 p3 = end;
    // Head : 3 circles
    vec2 c1  = circle_from_2_points(p1, p3, 1.25*body).zw;
    float d1 = length(texcoord - c1) - 1.25*body;
    vec2 c2  = circle_from_2_points(p2, p3, 1.25*body).xy;
    float d2 = length(texcoord - c2) - 1.25*body;
    vec2 c3  = circle_from_2_points(p1, p2, max(body-head, 1.0*body)).xy;
    float d3 = length(texcoord - c3) - max(body-head, 1.0*body);
    // Body : 1 segment
    float d4 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));
    // Outside (because of circles)
    if( texcoord.y > +(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.y < -(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.x < -(body/2.0 + antialias) )
         return 1000.0;
    if( texcoord.x > c1.x ) //(body + antialias) )
         return 1000.0;
    return min( d4, -min(d3,min(d1,d2)));
}

float arrow_triangle(vec2 texcoord,
                     float body, float head, float height,
                     float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    // Head : 3 lines
    float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
    float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
    float d3 = texcoord.x - end.x + head;
    // Body : 1 segment
    float d4 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));
    float d = min(max(max(d1, d2), -d3), d4);
    return d;
}

float arrow_triangle_90(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 1.0, linewidth, antialias);
}

float arrow_triangle_60(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 0.5, linewidth, antialias);
}

float arrow_triangle_30(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 0.25, linewidth, antialias);
}

float arrow_angle(vec2 texcoord,
                  float body, float head, float height,
                  float linewidth, float antialias)
{
    float d;
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    // Arrow tip (beyond segment end)
    if( texcoord.x > body/2.0) {
        // Head : 2 segments
        float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
        float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = end.x - texcoord.x;
        d = max(max(d1,d2), d3);
    } else {
        // Head : 2 segments
        float d1 = segment_distance(texcoord,
                                    end - head*vec2(+1.0,-height), end);
        float d2 = segment_distance(texcoord,
                                    end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = segment_distance(texcoord, start,
                                    end - vec2(linewidth,0.0));
        d = min(min(d1,d2), d3);
    }
    return d;
}

float arrow_angle_90(vec2 texcoord,
                     float body, float head,
                     float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 1.0, linewidth, antialias);
}

float arrow_angle_60(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 0.5, linewidth, antialias);
}

float arrow_angle_30(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 0.25, linewidth, antialias);
}

float arrow_stealth(vec2 texcoord,
                    float body, float head,
                    float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    float height = 0.5;
    // Head : 4 lines
    float d1 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end);
    float d2 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end-vec2(3.0*head/4.0,0.0));
    float d3 = line_distance(texcoord, end-head*vec2(+1.0,+height), end);
    float d4 = line_distance(texcoord, end-head*vec2(+1.0,+0.5),
                                       end-vec2(3.0*head/4.0,0.0));
    // Body : 1 segment
    float d5 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));
    return min(d5, max( max(-d1, d3), - max(-d2,d4)));
}

uniform vec2 iResolution;
uniform vec2 iMouse;
void main()
{
    const float M_PI = 3.14159265358979323846;
    const float SQRT_2 = 1.4142135623730951;
    const float linewidth = 3.0;
    const float antialias =  1.0;
    const float rows = 32.0;
    const float cols = 32.0;

    float body = min(iResolution.x/cols, iResolution.y/rows) / SQRT_2;
    vec2 texcoord = gl_FragCoord.xy;
    vec2 size   = iResolution.xy / vec2(cols,rows);
    vec2 center = (floor(texcoord/size) + vec2(0.5,0.5)) * size;
    texcoord -= center;
    float theta = M_PI-atan(center.y-iMouse.y,  center.x-iMouse.x);
    float cos_theta = cos(theta);
    float sin_theta = sin(theta);


    texcoord = vec2(cos_theta*texcoord.x - sin_theta*texcoord.y,
                    sin_theta*texcoord.x + cos_theta*texcoord.y);

    float d = arrow_stealth(texcoord, body, 0.25*body, linewidth, antialias);
    gl_FragColor = filled(d, linewidth, antialias, vec4(0,0,0,1));
}
"""


canvas = app.Canvas(size=(2*512, 2*512), keys='interactive')
canvas.context.set_state(blend=True, 
                         blend_func=('src_alpha', 'one_minus_src_alpha'),
                         blend_equation='func_add')


@canvas.connect
def on_draw(event):
    gloo.clear('white')
    program.draw('triangle_strip')


@canvas.connect
def on_resize(event):
    program["iResolution"] = event.size
    gloo.set_viewport(0, 0, event.size[0], event.size[1])


@canvas.connect
def on_mouse_move(event):
    x, y = event.pos
    program["iMouse"] = x, canvas.size[1] - y
    canvas.update()


program = gloo.Program(vertex, fragment, count=4)
dx, dy = 1, 1
program['position'] = (-dx, -dy), (-dx, +dy), (+dx, -dy), (+dx, +dy)
program["iMouse"] = (0., 0.)

if __name__ == '__main__':
    canvas.show()
    app.run()
