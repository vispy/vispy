// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

uniform int  log_scale_clamp;
uniform int  log_scale_discard;
uniform vec2 log_scale_range;
uniform vec2 log_scale_domain;
uniform float log_scale_base;

float forward(float value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;

    float v = log(value) / log(base);
    float t = (v - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    return sign(value) * (range.x + t*(range.y - range.x));
}

vec2 forward(vec2 value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;
    vec2 v = log(value) / log(base);
    vec2 t = (v - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    return sign(value) * (range.x + t*(range.y - range.x));
}

vec3 forward(vec3 value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;
    vec3 v = log(value) / log(base);
    vec3 t = (v - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    return sign(value) * (range.x + t*(range.y - range.x));
}


float inverse(float value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;
    float t = (abs(value) - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    float v = domain.x + t*(domain.y - domain.x);
    return sign(value) * pow(base, abs(v));
}

vec2 inverse(vec2 value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;
    vec2 t = (abs(value) - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    vec2 v = domain.x + t*(domain.y - domain.x);
    return sign(value) * pow(vec2(base), abs(v));
}

vec3 inverse(vec3 value)
{
    vec2 domain = log_scale_domain;
    vec2 range = log_scale_range;
    float base = log_scale_base;
    vec3 t = (abs(value) - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (log_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (log_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);
    vec3 v = domain.x + t*(domain.y - domain.x);
    return sign(value) * pow(vec3(base), abs(v));
}
