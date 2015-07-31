/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains the code for drawing complete triangles as arrow heads.
 * this includes triangles with a top corner of 30, 60 and 90 degrees.
 */

#include "arrowheads/util.glsl"

/**
 * Computes the signed distance to a triangle arrow. This is a helper function,
 * and in general you'll use arrow_triangle_30, arrow_triangle_60, or
 * arrow_triangle_90.
 *
 * Parameters:
 * -----------
 *
 * texcoord 
 *     Point to compute distance to
 * size
 *     Size of the arrow head in pixels
 * linewidth
 *     Width of the line
 * antialias
 *     Anti alias width
 * height
 *     Height of the head (pixel)
 * 
 * See also
 * --------
 * arrow_triangle_30, arrow_triangle_60, arrow_triangle_90
 *
 * Return:
 * -------
 * Signed distance to the arrow
 *
 */
float arrow_triangle(vec2 texcoord, float size, 
                     float linewidth, float antialias, float height)
{
    vec2 start = -vec2(size/2.0, 0.0);
    vec2 end   = +vec2(size/2.0, 0.0);

    // Head : 3 lines
    vec2 p1 = start + size*vec2(0.0, +height);
    vec2 p2 = start + size*vec2(0.0, -height);

    float d1 = line_distance(texcoord, end, p1);
    float d2 = line_distance(texcoord, p2, end);
    float d3 = start.x - texcoord.x;


    return max(max(d1, d2), d3);
}

/**
 * Returns the signed distance to an triangle arrow head with a tip corner
 * of 30 degrees.
 *
 * See also
 * --------
 * arrow_triangle, arrow_triangle_60, arrow_triangle_90
 */
float arrow_triangle_30(vec2 texcoord, float size,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, size, linewidth, antialias, 0.25);
}

/**
 * Returns the signed distance to an triangle arrow head with a tip corner
 * of 60 degrees.
 *
 * See also
 * --------
 * arrow_triangle, arrow_triangle_30, arrow_triangle_90
 */
float arrow_triangle_60(vec2 texcoord, float size,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, size, linewidth, antialias, 0.5);
}

/**
 * Returns the signed distance to an triangle arrow head with a tip corner
 * of 90 degrees.
 *
 * See also
 * --------
 * arrow_triangle, arrow_triangle_30, arrow_triangle_60
 */
float arrow_triangle_90(vec2 texcoord, float size,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, size, linewidth, antialias, 1.0);
}
