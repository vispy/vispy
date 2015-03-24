// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_heart(vec2 P, float size)
{
   float x = M_SQRT2/2.0 * (P.x - P.y);
   float y = M_SQRT2/2.0 * (P.x + P.y);
   float r1 = max(abs(x),abs(y))-size/3.5;
   float r2 = length(P - M_SQRT2/2.0*vec2(+1.0,-1.0)*size/3.5) - size/3.5;
   float r3 = length(P - M_SQRT2/2.0*vec2(-1.0,-1.0)*size/3.5) - size/3.5;
   return min(min(r1,r2),r3);
}
