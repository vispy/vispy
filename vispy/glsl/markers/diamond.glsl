// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_diamond(vec2 P, float size)
{
   float x = M_SQRT2/2.0 * (P.x - P.y);
   float y = M_SQRT2/2.0 * (P.x + P.y);
   return max(abs(x), abs(y)) - size/(2.0*M_SQRT2);
}
