// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "markers/disc.glsl"
#include "antialias/filled.glsl"

// Varyings
// ------------------------------------
varying float v_size;
varying vec4  v_color;

// Main
// ------------------------------------
void main()
{
    vec2 P = gl_PointCoord.xy - vec2(0.5,0.5);
    float point_size = v_size  + 2. * (1.0 + 1.5*1.0);
    float distance = marker_disc(P*point_size, v_size);
    gl_FragColor = filled(distance, 1.0, 1.0, v_color);
}
