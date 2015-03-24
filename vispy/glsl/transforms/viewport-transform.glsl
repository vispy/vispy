// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
uniform vec4 viewport;    // in pixels
uniform vec2 iResolution; // in pixels
vec4 transform(vec4 position)
{
    float w = viewport.z / iResolution.x;
    float h = viewport.w / iResolution.y;
    float x = 2.0*(viewport.x / iResolution.x) - 1.0 + w;
    float y = 2.0*(viewport.y / iResolution.y) - 1.0 + h;
    return  vec4((x + w*position.x/position.w)*position.w,
                 (y + h*position.y/position.w)*position.w,
                 position.z, position.w);
}
