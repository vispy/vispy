// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_infinity(vec2 P, float size)
{
    const vec2 c1 = vec2(+0.2125, 0.00);
    const vec2 c2 = vec2(-0.2125, 0.00);
    float r1 = length(P-c1*size) - size/3.5;
    float r2 = length(P-c1*size) - size/7.5;
    float r3 = length(P-c2*size) - size/3.5;
    float r4 = length(P-c2*size) - size/7.5;
    return min( max(r1,-r2), max(r3,-r4));
}
