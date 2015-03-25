// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

uniform mat4 view;
uniform mat4 model;
uniform mat4 projection;

vec4 transform(vec4 position)
{
    return projection*view*model*position;
}
