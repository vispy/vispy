// ----------------------------------------------------------------------------
// Copyright (c) Vispy Development Team
// Distributed under the (new) BSD License. See LICENSE.txt for more info.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position, ...)
//
// ----------------------------------------------------------------------------
#include "math/constants.glsl"

// Uniforms
// ------------------------------------
uniform float antialias;

// Attributes
// ------------------------------------
attribute vec2  v1;
attribute vec2  v2;
attribute float size;
attribute vec4  color;
attribute float linewidth;

// Varyings
// ------------------------------------
varying float v_size;
varying vec4  v_color;
varying vec2  v_orientation;
varying float v_antialias;
varying float v_linewidth;

// Main (hooked)
// ------------------------------------
void main (void)
{
    v_size        = size;
    v_linewidth   = linewidth;
    v_antialias   = antialias;
    v_color       = color;

    vec2 body = v2 - v1;
    v_orientation = (body / length(body));

    // Rotate 90 degrees, as arrow heads are by default oriented in the x
    // direction.
    v_orientation = vec2(-v_orientation.y, v_orientation.x);

    gl_Position = $transform(vec4(v2, 0, 1));
    gl_PointSize = M_SQRT2 * size + 2.0 * (linewidth + 1.5*antialias);
}
