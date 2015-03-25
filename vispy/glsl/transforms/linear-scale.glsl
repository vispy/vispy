// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
/*
  Linear scales are the most common scale, and a good default choice to map a
  continuous input domain to a continuous output range. The mapping is linear
  in that the output range value y can be expressed as a linear function of the
  input domain value x: y = mx + b. The input domain is typically a dimension
  of the data that you want to visualize, such as the height of students
  (measured in meters) in a sample population. The output range is typically a
  dimension of the desired output visualization, such as the height of bars
  (measured in pixels) in a histogram.
*/
uniform int  linear_scale_clamp;
uniform int  linear_scale_discard;
uniform vec2 linear_scale_range;
uniform vec2 linear_scale_domain;


float forward(float value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    float t = (value - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return range.x + t*(range.y - range.x);
}

vec2 forward(vec2 value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    vec2 t = (value - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return range.x + t*(range.y - range.x);
}

vec3 forward(vec3 value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    vec3 t = (value - domain.x) /(domain.y - domain.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return range.x + t*(range.y - range.x);
}

float inverse(float value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    float t = (value - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return domain.x + t*(domain.y - domain.x);
}

vec2 inverse(vec2 value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    vec2 t = (value - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return domain.x + t*(domain.y - domain.x);
}

vec3 inverse(vec3 value)
{
    vec2 domain = linear_scale_domain;
    vec2 range = linear_scale_range;
    vec3 t = (value - range.x) / (range.y - range.x);

#ifdef __FRAGMENT_SHADER__
    if (linear_scale_discard > 0)
        if (t != clamp(t, 0.0, 1.0))
            discard;
#endif

    if (linear_scale_clamp > 0)
        t = clamp(t, 0.0, 1.0);

    return domain.x + t*(domain.y - domain.x);
}
