/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains the vertex shader template for arrow heads.
 *
 * Variables
 * ---------
 * $transform
 *     Projection matrix of vertex to the screen
 *
 * Attributes
 * ----------
 * v1
 *     The first vertex of the arrow body
 * v2
 *     The second vertex of the arrow body. This will also be the center
 *     location of the arrow head. Using v1, we determine a direction vector
 *     to automatically determine the orientation.
 * size
 *     Size of the arrow head in pixels
 * color
 *     The color of the arrow head
 * v_linewidth
 *     The width for the stroke or outline of the shape.
 *
 * Varyings
 * --------
 * v_size
 *     The arrow head size in pixels
 * v_point_size
 *     The actual size of the point used for drawing. This is larger than the
 *     given arrow head size to make sure rotating goes well, and allows some
 *     space for anti-aliasing.
 * v_color
 *     The color for the arrow head
 * v_orientation
 *     A direction vector for the orientation of the arrow head
 * v_antialias
 *     Anti-alias width
 * v_linewidth
 *     Width for the stroke or outline of the shape.
 */

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
varying float v_point_size;
varying vec4  v_color;
varying vec2  v_orientation;
varying float v_antialias;
varying float v_linewidth;

// Main (hooked)
// ------------------------------------
void main (void)
{
    v_size        = size;
    v_point_size  = M_SQRT2 * size + 2.0 * (linewidth + 2.0*antialias);
    v_antialias   = antialias;
    v_color       = color;
    v_linewidth   = linewidth;

    vec2 body = v2 - v1;
    v_orientation = (body / length(body));
    v_orientation.y = -v_orientation.y;

    gl_Position = $transform(vec4(v2, 0, 1));
    gl_PointSize = v_point_size;
}
