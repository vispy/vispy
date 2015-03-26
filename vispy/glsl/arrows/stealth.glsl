// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "arrows/util.glsl"


/* ---------------------------------------------------------

   Computes the signed distance to an stealth arrow

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

float arrow_stealth(vec2 texcoord,
                    float body, float head,
                    float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    float height = 0.5;

    // Head : 4 lines
    float d1 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end);
    float d2 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end-vec2(3.0*head/4.0,0.0));
    float d3 = line_distance(texcoord, end-head*vec2(+1.0,+height), end);
    float d4 = line_distance(texcoord, end-head*vec2(+1.0,+0.5),
                                       end-vec2(3.0*head/4.0,0.0));

    // Body : 1 segment
    float d5 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));

    return min(d5, max( max(-d1, d3), - max(-d2,d4)));
}
