// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Externs
// ------------------------------------
// vec2 origin;
// vec2 position;
// vec2 texcoord;
// vec4 color;

// Varyings
// ------------------------------------
varying vec4  v_color;
varying float v_offset;
varying vec2  v_texcoord;

// Main
// ------------------------------------
void main()
{
    fetch_uniforms();

    gl_Position = <transform(origin)>;
    v_color = color;
    v_texcoord = texcoord;
    <viewport.transform>;

    // We set actual position after transform
    v_offset = 3.0*(offset + origin.x - int(origin.x));
    gl_Position = gl_Position + vec4(2.0*position/<viewport.viewport_global>.zw,0,0);
}
