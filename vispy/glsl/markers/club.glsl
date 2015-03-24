// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------
#include "math/constants.glsl"

float marker_club(vec2 P, float size)
{
    // clover (3 discs)
    const float t1 = -M_PI/2.0;
    const vec2  c1 = 0.225*vec2(cos(t1),sin(t1));
    const float t2 = t1+2*M_PI/3.0;
    const vec2  c2 = 0.225*vec2(cos(t2),sin(t2));
    const float t3 = t2+2*M_PI/3.0;
    const vec2  c3 = 0.225*vec2(cos(t3),sin(t3));
    float r1 = length( P - c1*size) - size/4.25;
    float r2 = length( P - c2*size) - size/4.25;
    float r3 = length( P - c3*size) - size/4.25;
    float r4 =  min(min(r1,r2),r3);

    // Root (2 circles and 2 planes)
    const vec2 c4 = vec2(+0.65, 0.125);
    const vec2 c5 = vec2(-0.65, 0.125);
    float r5 = length(P-c4*size) - size/1.6;
    float r6 = length(P-c5*size) - size/1.6;
    float r7 = P.y - 0.5*size;
    float r8 = 0.2*size - P.y;
    float r9 = max(-min(r5,r6), max(r7,r8));

    return min(r4,r9);
}
