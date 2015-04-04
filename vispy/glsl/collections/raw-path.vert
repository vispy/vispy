// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Externs
// ------------------------------------
// extern vec3  position;
// extern float id;
// extern vec4  color;
// vec4 transform(vec3 position);

// Varyings
// ------------------------------------
varying vec4 v_color;

// Main
// ------------------------------------
void main (void)
{
    fetch_uniforms();
    v_color = vec4(color.rgb, color.a*id);
    gl_Position = $transform(vec4(position, 1));
}
