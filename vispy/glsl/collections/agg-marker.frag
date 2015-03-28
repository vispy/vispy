// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <paint>  : "stroke", "filled" or "outline"
//  <marker> : "arrow", "asterisk", "chevron", "clover", "club",
//             "cross", "diamond", "disc", "ellipse", "hbar",
//             "heart", "infinity", "pin", "ring", "spade",
//             "square", "tag", "triangle", "vbar"
// ----------------------------------------------------------------------------
#include "math/constants.h"
#include "markers/markers.glsl"
#include "antialias/antialias.h"

// Varyings
// ------------------------------------
varying float v_antialias;
varying float v_linewidth;
varying float v_size;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying vec2  v_orientation;

// Main (hooked)
// ------------------------------------
void main()
{
    vec2 P = gl_PointCoord.xy - vec2(0.5,0.5);
    P = vec2(v_orientation.x*P.x - v_orientation.y*P.y,
             v_orientation.y*P.x + v_orientation.x*P.y);
    float point_size = SQRT_2*v_size  + 2. * (v_linewidth + 1.5*v_antialias);
    float distance = marker_<marker>(P*point_size, v_size);
    gl_FragColor = <paint>(distance, v_linewidth, v_antialias, v_fg_color, v_bg_color);
}
