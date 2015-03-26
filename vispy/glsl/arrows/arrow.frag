// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <paint>  : "stroke", "filled" or "outline"
//  <marker> : "steath", "curved",
//             "angle_30", "angle_60", "angle_90",
//             "triangle_30", "triangle_60", "triangle_90",
// ----------------------------------------------------------------------------
#include "math/constants.glsl"
#include "arrows/arrows.glsl"
#include "antialias/antialias.glsl"

// Varyings
// ------------------------------------
varying float v_antialias;
varying float v_linewidth;
varying float v_size;
varying float v_head;
varying float v_texcoord;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying vec2  v_orientation;

// Main (hooked)
// ------------------------------------
void main()
{
    vec2 P = gl_PointCoord.xy - vec2(0.5,0.5);
    P = vec2(v_orientation.x*P.x - v_orientation.y*P.y,
             v_orientation.y*P.x + v_orientation.x*P.y) * v_size;
    float point_size = M_SQRT2*v_size  + 2.0 * (v_linewidth + 1.5*v_antialias);
    float body = v_size/M_SQRT2;

    float distance = arrow_<arrow>(P, body, v_head*body, v_linewidth, v_antialias);
    gl_FragColor = <paint>(distance, v_linewidth, v_antialias, v_fg_color, v_bg_color);
}
