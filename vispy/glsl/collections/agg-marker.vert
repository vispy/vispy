// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position, ...)
//
// ----------------------------------------------------------------------------
#version 120
#include "math/constants.glsl"

// Collection externs
// ------------------------------------
// extern vec2  position;
// extern float size;
// extern vec4  fg_color;
// extern vec4  bg_color;
// extern float orientation;
// extern float antialias;
// extern float linewidth;


// Varyings
// ------------------------------------
varying float v_size;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying vec2  v_orientation;
varying float v_antialias;
varying float v_linewidth;


// Main (hooked)
// ------------------------------------
void main (void)
{
    fetch_uniforms();

    v_size        = size;
    v_linewidth   = linewidth;
    v_antialias   = antialias;
    v_fg_color    = fg_color;
    v_bg_color    = bg_color;
    v_orientation = vec2(cos(orientation), sin(orientation));

    gl_Position = <transform>;
    gl_PointSize = M_SQRT2 * size + 2.0 * (linewidth + 1.5*antialias);
}
