/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains the shader code for drawing "angle" arrow heads, which
 * are drawn as two lines moving away from the arrow tip under a certain
 * angle.
 */

#include "arrowheads/util.glsl"

/* ---------------------------------------------------------

   Computes the signed distance to an angle arrow

   Parameters:
   -----------

   texcoord : Point to compute distance to
   body :     Total length of the arrow (pixels, body+head)
   head :     Length of the head (pixels)
   height :   Height of the head (pixel)
   linewidth: Stroke line width (in pixels)
   antialias: Stroke antialiased area (in pixels)

   Return:
   -------
   Signed distance to the arrow

   --------------------------------------------------------- */
float arrow_angle(vec2 texcoord, float size, float height)
{
    float d;
    vec2 start = -vec2(size/2.0, 0.0);
    vec2 end   = +vec2(size/2.0, 0.0);

    vec2 p1 = start + size*vec2(0.0, +height);
    vec2 p2 = start + size*vec2(0.0, -height);

    // Arrow tip (beyond segment end)
    if( texcoord.x > size/2.0) {
        // Head : 2 segments
        float d1 = line_distance(texcoord, end, p1);
        float d2 = line_distance(texcoord, p2, end);
        // Body : 1 segment
        float d3 = end.x - texcoord.x;
        d = max(max(d1,d2), d3);
    } else {
        // Head : 2 segments
        float d1 = segment_distance(texcoord, p1, end);
        float d2 = segment_distance(texcoord, p2, end);
        // Body : 1 segment
        float d3 = segment_distance(texcoord, vec2(0.0, 0.0), end);
        d = min(min(d1,d2), d3);
    }
    return d;
}

float arrow_angle_30(vec2 texcoord, float size)
{
    return arrow_angle(texcoord, size, 0.25);
}

float arrow_angle_60(vec2 texcoord, float size)
{
    return arrow_angle(texcoord, size, 0.5);
}

float arrow_angle_90(vec2 texcoord, float size)
{
    return arrow_angle(texcoord, size, 1.0);
}
