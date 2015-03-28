// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_arrow(vec2 P, float size)
{
    float r1 = abs(P.x) + abs(P.y) - size/2;
    float r2 = max(abs(P.x+size/2), abs(P.y)) - size/2;
    float r3 = max(abs(P.x-size/6)-size/4, abs(P.y)- size/4);
    return min(r3,max(.75*r1,r2));
}
