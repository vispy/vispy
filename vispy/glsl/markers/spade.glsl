// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_spade(vec2 P, float size)
{
   // Reversed heart (diamond + 2 circles)
   float s= size * 0.85 / 3.5;
   float x = M_SQRT2/2.0 * (P.x + P.y) + 0.4*s;
   float y = M_SQRT2/2.0 * (P.x - P.y) - 0.4*s;
   float r1 = max(abs(x),abs(y)) - s;
   float r2 = length(P - M_SQRT2/2.0*vec2(+1.0,+0.2)*s) - s;
   float r3 = length(P - M_SQRT2/2.0*vec2(-1.0,+0.2)*s) - s;
   float r4 =  min(min(r1,r2),r3);

   // Root (2 circles and 2 planes)
   const vec2 c1 = vec2(+0.65, 0.125);
   const vec2 c2 = vec2(-0.65, 0.125);
   float r5 = length(P-c1*size) - size/1.6;
   float r6 = length(P-c2*size) - size/1.6;
   float r7 = P.y - 0.5*size;
   float r8 = 0.1*size - P.y;
   float r9 = max(-min(r5,r6), max(r7,r8));

    return min(r4,r9);
}
