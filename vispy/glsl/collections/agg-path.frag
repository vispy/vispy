// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/antialias.glsl"
#include "antialias/caps.glsl"

// Varyings
// ------------------------------------
varying vec2  v_caps;
varying vec4  v_color;
varying float v_length;
varying vec2  v_texcoord;
varying float v_linewidth;
varying float v_antialias;
varying float v_miter_limit;
varying vec2  v_bevel_distance;

void main()
{
    float distance = v_texcoord.y;

    if (v_caps.x < 0.0)
    {
        gl_FragColor = cap(1, v_texcoord.x, v_texcoord.y,
                           v_linewidth, v_antialias, v_color);
        // Do not return here or clipping won't be enforced
        // return;
    }
    else if (v_caps.y > v_length)
    {
        gl_FragColor = cap(1, v_texcoord.x-v_length, v_texcoord.y,
                           v_linewidth, v_antialias, v_color);
        // Do not return here or clipping won't be enforced
        // return;
    }

    // Round join (instead of miter)
    // if (v_texcoord.x < 0.0)          { distance = length(v_texcoord); }
    // else if(v_texcoord.x > v_length) { distance = length(v_texcoord - vec2(v_length, 0.0)); }

    else {
        // Miter limit
        float t = (v_miter_limit-1.0)*(v_linewidth/2.0) + v_antialias;
        if( (v_texcoord.x < 0.0) && (v_bevel_distance.x > (abs(distance) + t)) )
        {
            distance = v_bevel_distance.x - t;
        }
        else if( (v_texcoord.x > v_length) && (v_bevel_distance.y > (abs(distance) + t)) )
        {
            distance = v_bevel_distance.y - t;
        }
        gl_FragColor = stroke(distance, v_linewidth, v_antialias, v_color);
    }
}
