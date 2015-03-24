// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/stroke.glsl"


/* ---------------------------------------------------------
   Compute antialiased fragment color for a line cap.
   Type: square

   Parameters:
   -----------

   dx,dy    : signed distances to cap point (in pixels)
   linewidth: Stroke line width (in pixels)
   antialias: Stroke antialiased area (in pixels)
   stroke:    Stroke color

   Return:
   -------
   Fragment color (vec4)

   --------------------------------------------------------- */
vec4 cap_square(float dx, float dy, float linewidth, float antialias, vec4 color)
{
    float t = linewidth/2.0 - antialias;
    float d = max(abs(dx),abs(dy));
    return stroke(d, linewidth, antialias, color);
}
