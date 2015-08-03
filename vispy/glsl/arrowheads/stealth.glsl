/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains the code for drawing "stealth" type arrow heads.
 */

#include "arrowheads/util.glsl"


/**
 * Computes the signed distance to an stealth arrow
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
 *
 * Return:
 * -------
 * Signed distance to the arrow
 */
float arrow_stealth(vec2 texcoord, float size, 
                    float linewidth, float antialias)
{
    vec2 start = -vec2(size/2.0, 0.0);
    vec2 end   = +vec2(size/2.0, 0.0);
    float height = 0.5;

    // Head : 4 lines
    float d1 = line_distance(texcoord, start + size*vec2(0.0, +height), end);
    float d2 = line_distance(texcoord, start + size*vec2(0.0, +height),
                             start + size*vec2(0.3, 0.0));
    float d3 = line_distance(texcoord, start + size*vec2(0.0, -height), end);
    float d4 = line_distance(texcoord, start + size*vec2(0.0, -height),
                             start + size*vec2(0.25, 0.0));

    return max( max(-d1, d3), - max(-d2,d4));
}
