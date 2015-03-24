// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_pin(vec2 P, float size)
{
    size *= .9;

    vec2 c1 = vec2(0.0,-0.15)*size;
    float r1 = length(P-c1)-size/2.675;
    vec2 c2 = vec2(+1.49,-0.80)*size;
    float r2 = length(P-c2) - 2.*size;
    vec2 c3 = vec2(-1.49,-0.80)*size;
    float r3 = length(P-c3) - 2.*size;
    float r4 = length(P-c1)-size/5;
    return max( min(r1,max(max(r2,r3),-P.y)), -r4);
}
