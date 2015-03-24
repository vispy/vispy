// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_chevron(vec2 P, float size)
{
    float x = 1.0/M_SQRT2 * ((P.x-size/6) - P.y);
    float y = 1.0/M_SQRT2 * ((P.x-size/6) + P.y);
    float r1 = max(abs(x),          abs(y))          - size/3.0;
    float r2 = max(abs(x-size/3.0), abs(y-size/3.0)) - size/3.0;
    return max(r1,-r2);
}
