/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This files contains the code for drawing curved arrow heads.
 */

#include "arrowheads/util.glsl"

/**
 * Computes the signed distance to an curved arrow
 *
 * Parameters:
 * -----------
 * texcoord 
 *     Point to compute distance to
 * size 
 *     size of the arrow head in pixels
 * linewidth
 *     Width of the line
 * antialias
 *     Anti alias width
 *
 * Return:
 * -------
 * Signed distance to the arrow
 *
 */
float arrow_curved(vec2 texcoord, float size, float linewidth, float antialias)
{
    vec2 start = -vec2(size/2, 0.0);
    vec2 end   = +vec2(size/2, 0.0);
    float height = 0.5;

    vec2 p1 = start + size*vec2(0, -height);
    vec2 p2 = start + size*vec2(0, +height);
    vec2 p3 = end;

    // Head : 3 circles
    vec2 c1  = circle_from_2_points(p1, p3, 6.0*size).zw;
    float d1 = length(texcoord - c1) - 6*size;
    vec2 c2  = circle_from_2_points(p2, p3, 6.0*size).xy;
    float d2 = length(texcoord - c2) - 6*size;
    vec2 c3  = circle_from_2_points(p1, p2, 3.0*size).xy;
    float d3 = length(texcoord - c3) - 3*size;

    return -min(d3, min(d1,d2));
}
