// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/antialias.glsl"

// Varyings
// ------------------------------------
varying vec4  v_color;
varying float v_distance;
varying float v_linewidth;
varying float v_antialias;

// Main
// ------------------------------------
void main()
{
    if (v_color.a == 0.)  { discard; }
    gl_FragColor = stroke(v_distance, v_linewidth, v_antialias, v_color);
}
