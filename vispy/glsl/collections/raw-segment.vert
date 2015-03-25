// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position)
//
// ----------------------------------------------------------------------------

// Externs
// ------------------------------------
// extern vec2 P;
// extern vec4 color;

// Varyings
// ------------------------------------
varying vec4  v_color;



// Main
// ------------------------------------
void main (void)
{
    // This function is externally generated
    fetch_uniforms();
    v_color     = color;

    gl_Position = <transform(P)>;

    <viewport.transform>;
}
