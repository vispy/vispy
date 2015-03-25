// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_square(vec2 P, float size)
{
    return max(abs(P.x), abs(P.y)) - size/2.0;
}
