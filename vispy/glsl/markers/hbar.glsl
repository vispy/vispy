// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

float marker_hbar(vec2 P, float size)
{
    return max(abs(P.x)- size/6.0, abs(P.y)- size/2.0);
}
