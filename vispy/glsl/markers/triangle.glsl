// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_triangle(vec2 P, float size)
{
    float x = M_SQRT2/2.0 * (P.x - (P.y-size/6));
    float y = M_SQRT2/2.0 * (P.x + (P.y-size/6));
    float r1 = max(abs(x), abs(y)) - size/(2.0*M_SQRT2);
    float r2 = P.y-size/6;
    return max(r1,r2);
}
