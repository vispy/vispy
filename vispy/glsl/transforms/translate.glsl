// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
uniform vec3 translate_translate;

vec2 forward(float x, float y)
{ return vec2(x,y) + translate_translate.xy; }

vec2 forward(vec2 P)
{ return P + translate_translate.xy; }

vec3 forward(float x, float y, float z)
{ return vec3(x,y,z) + translate_translate); }

vec3 forward(vec3 P)
{ return P + translate_translate; }

vec4 forward(vec4 P)
{ return vec4(P.xyz + translate_translate, P.w); }

vec2 inverse(float x, float y)
{ return vec2(x,y) - translate_translate.xy; }

vec2 inverse(vec2 P)
{ return P - translate_translate.xy; }

vec3 inverse(float x, float y, float z)
{ return vec3(x,y,z) - translate_translate); }

vec3 inverse(vec3 P)
{ return P - translate_translate; }

vec4 inverse(vec4 P)
{ return vec4(P.xyz - translate_translate, P.w); }
