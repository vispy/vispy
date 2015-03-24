// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_cross(vec2 P, float size)
{
    float x = M_SQRT2/2.0 * (P.x - P.y);
    float y = M_SQRT2/2.0 * (P.x + P.y);
    float r1 = max(abs(x - size/3.0), abs(x + size/3.0));
    float r2 = max(abs(y - size/3.0), abs(y + size/3.0));
    float r3 = max(abs(x), abs(y));
    float r = max(min(r1,r2),r3);
    r -= size/2;
    return r;
}
