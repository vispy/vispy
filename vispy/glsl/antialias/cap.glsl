// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "antialias/stroke.glsl"

// Cap types
// ----------------------------
const int CAP_NONE         = 0;
const int CAP_ROUND        = 1;
const int CAP_TRIANGLE_IN  = 2;
const int CAP_TRIANGLE_OUT = 3;
const int CAP_SQUARE       = 4;
const int CAP_BUTT         = 5;


/* ---------------------------------------------------------
   Compute antialiased fragment color for a line cap.
   Require the stroke function.

   Parameters:
   -----------

   type     : Type of cap
   dx,dy    : signed distances to cap point (in pixels)
   linewidth: Stroke line width (in pixels)
   antialias: Stroke antialiased area (in pixels)
   stroke:    Stroke color

   Return:
   -------
   Fragment color (vec4)

   --------------------------------------------------------- */
vec4 cap(int type, float dx, float dy, float linewidth, float antialias, vec4 color)
{
    float d = 0.0;
    dx = abs(dx);
    dy = abs(dy);
    float t = linewidth/2.0 - antialias;

    // Round
    if (type == CAP_ROUND)
        d = sqrt(dx*dx+dy*dy);

    // Square
    else if (type == CAP_SQUARE)
        d = max(dx,dy);

    // Butt
    else if (type == CAP_BUTT)
        d = max(dx+t,dy);

    // Triangle in
    else if (type == CAP_TRIANGLE_IN)
        d = (dx+abs(dy));

    // Triangle out
    else if (type == CAP_TRIANGLE_OUT)
        d = max(abs(dy),(t+dx-abs(dy)));

    // None
    else
        discard;

    return stroke(d, linewidth, antialias, color);
}
