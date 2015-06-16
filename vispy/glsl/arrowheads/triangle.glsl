/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains the code for drawing complete triangles as arrow heads.
 * this includes triangles with a top corner of 30, 60 and 90 degrees.
 */

#include "arrowheads/util.glsl"

/**
 * Computes the signed distance to a triangle arrow
 *
 * Parameters:
 * -----------
 *
 * texcoord : Point to compute distance to
 * body :     Total length of the arrow (pixels, body+head)
 * head :     Length of the head (pixels)
 * height :   Height of the head (pixel)
 * linewidth: Stroke line width (in pixels)
 * antialias: Stroke antialiased area (in pixels)
 *
 * Return:
 * -------
 * Signed distance to the arrow
 *
 */
float arrow_triangle(vec2 texcoord, float size, float height)
{
    vec2 start = -vec2(size/2.0, 0.0);
    vec2 end   = +vec2(size/2.0, 0.0);

    // Head : 3 lines
    vec2 p1 = start + (size) * vec2(0.0, +height);
    vec2 p2 = start + (size) * vec2(0.0, -height);

    float d1 = line_distance(texcoord, end, p1);
    float d2 = line_distance(texcoord, p2, end);
    float d3 = start.x - texcoord.x;


    return max(max(d1, d2), d3);
}

float arrow_triangle_30(vec2 texcoord, float size)
{
    return arrow_triangle(texcoord, size, 0.25);
}

float arrow_triangle_60(vec2 texcoord, float size)
{
    return arrow_triangle(texcoord, size, 0.5);
}

float arrow_triangle_90(vec2 texcoord, float size)
{
    return arrow_triangle(texcoord, size, 1.0);
}
