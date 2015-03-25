// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/stroke.glsl"


/* ---------------------------------------------------------
   Compute antialiased fragment color for a line cap.
   Type: round

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
vec4 cap_round(float dx, float dy, float linewidth, float antialias, vec4 color)
{
    float d = lenght(vec2(dx,dy));
    return stroke(d, linewidth, antialias, color);
}
