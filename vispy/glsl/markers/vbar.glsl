// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_vbar(vec2 P, float size)
{
    return max(abs(P.y)- size/2.0, abs(P.x)- size/6.0);
}
