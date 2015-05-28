// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "math/signed-line-distance.glsl"
#include "math/point-to-line-distance.glsl"
#include "math/signed-segment-distance.glsl"
#include "math/circle-through-2-points.glsl"
#include "math/point-to-line-projection.glsl"


/* ---------------------------------------------------------

   Computes the signed distance to a triangle arrow

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

float arrow_triangle(vec2 texcoord,
                     float body, float head, float height,
                     float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);

    // Head : 3 lines
    float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
    float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
    float d3 = texcoord.x - end.x + head;

    // Body : 1 segment
    float d4 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));

    float d = min(max(max(d1, d2), -d3), d4);
    return d;
}


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
float arrow_angle(vec2 texcoord,
                  float body, float head, float height,
                  float linewidth, float antialias)
{
    float d;
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);

    // Arrow tip (beyond segment end)
    if( texcoord.x > body/2.0) {
        // Head : 2 segments
        float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
        float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = end.x - texcoord.x;
        d = max(max(d1,d2), d3);
    } else {
        // Head : 2 segments
        float d1 = segment_distance(texcoord, end - head*vec2(+1.0,-height), end);
        float d2 = segment_distance(texcoord, end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));
        d = min(min(d1,d2), d3);
    }
    return d;
}
