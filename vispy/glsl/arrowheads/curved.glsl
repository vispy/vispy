// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "arrowheads/util.glsl"


/* ---------------------------------------------------------

   Computes the signed distance to an curved arrow

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

float arrow_curved(vec2 texcoord,
                   float size,
                   float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(size/2.0, 0.0);
    vec2 end   = +vec2(size/2.0, 0.0);
    float height = 0.5;

    vec2 p1 = end - size*vec2(+1.0,+height);
    vec2 p2 = end - size*vec2(+1.0,-height);
    vec2 p3 = end;

    // Head : 3 circles
    vec2 c1  = circle_from_2_points(p1, p3, 1.25*size).zw;
    float d1 = length(texcoord - c1) - 1.25*size;
    vec2 c2  = circle_from_2_points(p2, p3, 1.25*size).xy;
    float d2 = length(texcoord - c2) - 1.25*size;
    vec2 c3  = circle_from_2_points(p1, p2, 1.25*size).xy;
    float d3 = length(texcoord - c3) - 1.25*size;

    // Outside (because of circles)
    if( texcoord.y > +(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.y < -(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.x > c1.x ) //(size + antialias) )
         return 1000.0;

    return min(d3,min(d1,d2)));
}
