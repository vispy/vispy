// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

float get_x(float x)
{
    return x;
}

float get_x(vec2 xy)
{
    return xy.x;
}

float get_x(vec3 xyz)
{
    return xyz.x;
}

float get_x(vec4 xyzw)
{
    return xyzw.x;
}
