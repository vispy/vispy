// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#version 120

// Uniform
// ------------------------------------
uniform mat4  u_projection;
uniform float u_antialias;

// Attributes
// ------------------------------------
attribute float a_size;
attribute float a_orientation;
attribute float a_linewidth;
attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;

// Varyings
// ------------------------------------
varying float v_antialias;
varying float v_linewidth;
varying float v_size;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying vec2  v_rotation;

void main (void)
{
    v_size = a_size;
    v_linewidth = 2.5*a_linewidth;
    v_antialias = 3.0*u_antialias;
    v_fg_color = a_fg_color;
    v_bg_color = a_bg_color;
    v_rotation = vec2(cos(a_orientation), sin(a_orientation));

    gl_Position = u_projection * vec4(a_position, 1.0);
    gl_PointSize = a_size + 2*(a_linewidth + 1.5*v_antialias);
}
