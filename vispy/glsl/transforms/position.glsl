// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

vec4 position(float x)
{
    return vec4(x, 0.0, 0.0, 1.0);
}

vec4 position(float x, float y)
{
    return vec4(x, y, 0.0, 1.0);
}

vec4 position(vec2 xy)
{
    return vec4(xy, 0.0, 1.0);
}

vec4 position(float x, float y, float z)
{
    return vec4(x, y, z, 1.0);
}

vec4 position(vec3 xyz)
{
    return vec4(xyz, 1.0);
}

vec4 position(vec4 xyzw)
{
    return xyzw;
}

vec4 position(vec2 xy, float z)
{
    return vec4(xy, z, 1.0);
}

vec4 position(float x, vec2 yz)
{
    return vec4(x, yz, 1.0);
}
