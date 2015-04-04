// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position, ...)
//
// ----------------------------------------------------------------------------
#include "misc/viewport-NDC.glsl"

// Externs
// ------------------------------------
// extern vec3  P0;
// extern vec3  P1;
// extern float index;
// extern vec4  color;
// extern float antialias;
// extern float linewidth;
// extern vec4  viewport;
// vec4 transform(vec3 position);

// Varyings
// ------------------------------------
varying float v_length;
varying float v_antialias;
varying float v_linewidth;
varying vec2  v_texcoord;
varying vec4  v_color;



// Main
// ------------------------------------
void main (void)
{
    // This function is externally generated
    fetch_uniforms();
    v_linewidth = linewidth;
    v_antialias = antialias;
    v_color     = color;

    vec4 P0_ = $transform(vec4(P0, 1));
    vec4 P1_ = $transform(vec4(P1, 1));

    // p0/p1 in viewport coordinates
    vec2 p0 = NDC_to_viewport(P0_, viewport.zw);
    vec2 p1 = NDC_to_viewport(P1_, viewport.zw);

    //
    vec2 position;
    vec2 T = p1 - p0;
    v_length = length(T);
    float w = v_linewidth/2.0 + 1.5*v_antialias;
    T = w*normalize(T);
    float z;
    if( index < 0.5 ) {
       position = vec2( p0.x-T.y-T.x, p0.y+T.x-T.y);
       v_texcoord = vec2(-w, +w);
       z = P0.z;
    } else if( index < 1.5 ) {
       position = vec2(p0.x+T.y-T.x, p0.y-T.x-T.y);
       v_texcoord= vec2(-w, -w);
       z = P0.z;
    } else if( index < 2.5 ) {
       position = vec2( p1.x+T.y+T.x, p1.y-T.x+T.y);
       v_texcoord= vec2(v_length+w, -w);
       z = P1.z;
    } else {
       position = vec2( p1.x-T.y+T.x, p1.y+T.x+T.y);
       v_texcoord = vec2(v_length+w, +w);
       z = P1.z;
    }

    gl_Position = viewport_to_NDC(vec3(position,z), viewport.zw);
}
