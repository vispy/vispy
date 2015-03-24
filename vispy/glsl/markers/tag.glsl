// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_tag(vec2 P, float size)
{
    float r1 = max(abs(P.x)- size/2.0, abs(P.y)- size/6.0);
    float r2 = abs(P.x-size/2.0)+abs(P.y)-size;
    return max(r1,.75*r2);
}
