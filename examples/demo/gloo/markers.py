# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Marker shader definitions. You need to combine marker_frag with one of the
available marker function (marker_disc, marker_diamond, ...)
"""


vert = """
#version 120

// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
uniform float u_size;

// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_linewidth;
attribute float a_size;

// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_size = a_size * u_size;
    v_linewidth = a_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = u_projection * u_view * u_model *
        vec4(a_position*u_size,1.0);
    gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
}
"""


frag = """
#version 120

// Constants
// ------------------------------------

// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

// Functions
// ------------------------------------
float marker(vec2 P, float size);


// Main
// ------------------------------------
void main()
{
    float size = v_size +2*(v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;

    // The marker function needs to be linked with this shader
    float r = marker(gl_PointCoord, size);

    float d = abs(r) - t;
    if( r > (v_linewidth/2.0+v_antialias))
    {
        discard;
    }
    else if( d < 0.0 )
    {
       gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


disc = """
float marker(vec2 P, float size)
{
    float r = length((P.xy - vec2(0.5,0.5))*size);
    r -= v_size/2;
    return r;
}
"""


arrow = """
float marker(vec2 P, float size)
{
    float r1 = abs(P.x -.50)*size + abs(P.y -.5)*size - v_size/2;
    float r2 = abs(P.x -.25)*size + abs(P.y -.5)*size - v_size/2;
    float r = max(r1,-r2);
    return r;
}
"""


ring = """
float marker(vec2 P, float size)
{
    float r1 = length((P.xy - vec2(0.5,0.5))*size) - v_size/2;
    float r2 = length((P.xy - vec2(0.5,0.5))*size) - v_size/4;
    float r = max(r1,-r2);
    return r;
}
"""


clobber = """
float marker(vec2 P, float size)
{
    const float PI = 3.14159265358979323846264;
    const float t1 = -PI/2;
    const vec2  c1 = 0.2*vec2(cos(t1),sin(t1));
    const float t2 = t1+2*PI/3;
    const vec2  c2 = 0.2*vec2(cos(t2),sin(t2));
    const float t3 = t2+2*PI/3;
    const vec2  c3 = 0.2*vec2(cos(t3),sin(t3));

    float r1 = length((P.xy- vec2(0.5,0.5) - c1)*size);
    r1 -= v_size/3;
    float r2 = length((P.xy- vec2(0.5,0.5) - c2)*size);
    r2 -= v_size/3;
    float r3 = length((P.xy- vec2(0.5,0.5) - c3)*size);
    r3 -= v_size/3;
    float r = min(min(r1,r2),r3);
    return r;
}
"""


square = """
float marker(vec2 P, float size)
{
    float r = max(abs(P.x -.5)*size, abs(P.y -.5)*size);
    r -= v_size/2;
    return r;
}
"""


diamond = """
float marker(vec2 P, float size)
{
    float r = abs(P.x -.5)*size + abs(P.y -.5)*size;
    r -= v_size/2;
    return r;
}
"""


vbar = """
float marker(vec2 P, float size)
{
    float r1 = max(abs(P.x - 0.75)*size, abs(P.x - 0.25)*size);
    float r3 = max(abs(P.x - 0.50)*size, abs(P.y - 0.50)*size);
    float r = max(r1,r3);
    r -= v_size/2;
    return r;
}
"""


hbar = """
float marker(vec2 P, float size)
{
    float r2 = max(abs(P.y - 0.75)*size, abs(P.y - 0.25)*size);
    float r3 = max(abs(P.x - 0.50)*size, abs(P.y - 0.50)*size);
    float r = max(r2,r3);
    r -= v_size/2;
    return r;
}
"""


cross = """
float marker(vec2 P, float size)
{
    float r1 = max(abs(P.x - 0.75)*size, abs(P.x - 0.25)*size);
    float r2 = max(abs(P.y - 0.75)*size, abs(P.y - 0.25)*size);
    float r3 = max(abs(P.x - 0.50)*size, abs(P.y - 0.50)*size);
    float r = max(min(r1,r2),r3);
    r -= v_size/2;
    return r;
}
"""

tailed_arrow = """
float marker(vec2 P, float size)
{

   //arrow_right
    float r1 = abs(P.x -.50)*size + abs(P.y -.5)*size - v_size/2;
    float r2 = abs(P.x -.25)*size + abs(P.y -.5)*size - v_size/2;
    float arrow = max(r1,-r2);

    //hbar
    float r3 = (abs(P.y-.5)*2+.3)*v_size-v_size/2;
    float r4 = (P.x -.775)*size;
    float r6 = abs(P.x -.5)*size-v_size/2;
    float limit = (P.x -.5)*size + abs(P.y -.5)*size - v_size/2;
    float hbar = max(limit,max(max(r3,r4),r6));

    return min(arrow,hbar);
}
"""
