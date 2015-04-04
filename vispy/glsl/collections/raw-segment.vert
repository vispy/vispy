// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Externs
// ------------------------------------
// extern vec3 position;
// extern vec4 color;
// extern vec4 viewport;
// vec4 transform(vec3 position);

// Varyings
// ------------------------------------
varying vec4 v_color;

// Main
// ------------------------------------
void main (void)
{
    // This function is externally generated
    fetch_uniforms();
    v_color = color;

    gl_Position = $transform(vec4(position, 1));
}
