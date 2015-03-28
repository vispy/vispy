// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/caps.glsl"
#include "antialias/antialias.glsl"

// Varyings
// ------------------------------------
varying float v_length;
varying float v_linewidth;
varying float v_antialias;
varying vec2  v_texcoord;
varying vec4  v_color;


// Main
// ------------------------------------
void main (void)
{
    if (v_texcoord.x < 0.0) {
        gl_FragColor = cap( CAP_ROUND,
                            v_texcoord.x, v_texcoord.y,
                            v_linewidth, v_antialias, v_color);
    } else if(v_texcoord.x > v_length) {
        gl_FragColor = cap( CAP_ROUND,
                            v_texcoord.x-v_length, v_texcoord.y,
                            v_linewidth, v_antialias, v_color);
    } else {
        gl_FragColor = stroke(v_texcoord.y, v_linewidth, v_antialias, v_color);
    }
}
