// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Externs
// ------------------------------------
// extern vec3 position;
// extern float size;
// extern vec4 fg_color;
// extern vec4 bg_color;
// extern float orientation;
// extern float antialias;
// extern float linewidth;
// extern vec4 transform(vec3);

// Varyings
// ------------------------------------
varying float v_size;
varying vec4  v_color;
varying float v_linewidth;
varying float v_antialias;

// Main (hooked)
// ------------------------------------
void main (void)
{
    fetch_uniforms();

    v_size = size;
    v_color = color;

    gl_Position = $transform(vec4(position, 1));
    gl_PointSize = size + 2.0 * (1.0 + 1.5*1.0);
}
