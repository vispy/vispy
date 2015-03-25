// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
uniform vec2 panzoom_scale;
uniform vec2 panzoom_translate;
vec4 panzoom(vec4 position)
{
    return vec4(panzoom_scale*position.xy + panzoom_translate, position.z, 1.0);
}
