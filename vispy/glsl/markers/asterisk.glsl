// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_asterisk(vec2 P, float size)
{
    float x = M_SQRT2/2 * (P.x - P.y);
    float y = M_SQRT2/2 * (P.x + P.y);
    float r1 = max(abs(x)- size/2, abs(y)- size/10);
    float r2 = max(abs(y)- size/2, abs(x)- size/10);
    float r3 = max(abs(P.x)- size/2, abs(P.y)- size/10);
    float r4 = max(abs(P.y)- size/2, abs(P.x)- size/10);
    return min( min(r1,r2), min(r3,r4));
}
