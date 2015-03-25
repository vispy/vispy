/* -------------------------------------------------------------------------
 * Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
 * Distributed under the (new) BSD License.
 * -------------------------------------------------------------------------
 */

// Computes the signed distance from a line
float line_distance(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    return dot(rel_p, vec2(dir.y, -dir.x));
}

// Computes the signed distance from a line segment
float segment_distance(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    float dist1 = abs(dot(rel_p, vec2(dir.y, -dir.x)));
    float dist2 = abs(dot(rel_p, dir)) - 0.5*len;
    return max(dist1, dist2);
}

// Computes the center with given radius passing through p1 & p2
vec4 circle_from_2_points(vec2 p1, vec2 p2, float radius)
{
    float q = length(p2-p1);
    vec2 m = (p1+p2)/2.0;
    vec2 d = vec2( sqrt(radius*radius - (q*q/4.0)) * (p1.y-p2.y)/q,
                   sqrt(radius*radius - (q*q/4.0)) * (p2.x-p1.x)/q);
    return  vec4(m+d, m-d);
}

float arrow_curved(vec2 texcoord,
                   float body, float head,
                   float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    float height = 0.5;

    vec2 p1 = end - head*vec2(+1.0,+height);
    vec2 p2 = end - head*vec2(+1.0,-height);
    vec2 p3 = end;

    // Head : 3 circles
    vec2 c1  = circle_from_2_points(p1, p3, 1.25*body).zw;
    float d1 = length(texcoord - c1) - 1.25*body;
    vec2 c2  = circle_from_2_points(p2, p3, 1.25*body).xy;
    float d2 = length(texcoord - c2) - 1.25*body;
    vec2 c3  = circle_from_2_points(p1, p2, max(body-head, 1.0*body)).xy;
    float d3 = length(texcoord - c3) - max(body-head, 1.0*body);

    // Body : 1 segment
    float d4 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));

    // Outside (because of circles)
    if( texcoord.y > +(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.y < -(2.0*head + antialias) )
         return 1000.0;
    if( texcoord.x < -(body/2.0 + antialias) )
         return 1000.0;
    if( texcoord.x > c1.x ) //(body + antialias) )
         return 1000.0;

    return min( d4, -min(d3,min(d1,d2)));
}

float arrow_triangle(vec2 texcoord,
                     float body, float head, float height,
                     float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);

    // Head : 3 lines
    float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
    float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
    float d3 = texcoord.x - end.x + head;

    // Body : 1 segment
    float d4 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));

    float d = min(max(max(d1, d2), -d3), d4);
    return d;
}

float arrow_triangle_90(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 1.0, linewidth, antialias);
}

float arrow_triangle_60(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 0.5, linewidth, antialias);
}

float arrow_triangle_30(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 0.25, linewidth, antialias);
}

float arrow_angle(vec2 texcoord,
                  float body, float head, float height,
                  float linewidth, float antialias)
{
    float d;
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);

    // Arrow tip (beyond segment end)
    if( texcoord.x > body/2.0) {
        // Head : 2 segments
        float d1 = line_distance(texcoord, end, end - head*vec2(+1.0,-height));
        float d2 = line_distance(texcoord, end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = end.x - texcoord.x;
        d = max(max(d1,d2), d3);
    } else {
        // Head : 2 segments
        float d1 = segment_distance(texcoord, end - head*vec2(+1.0,-height), end);
        float d2 = segment_distance(texcoord, end - head*vec2(+1.0,+height), end);
        // Body : 1 segment
        float d3 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));
        d = min(min(d1,d2), d3);
    }
    return d;
}

float arrow_angle_90(vec2 texcoord,
                     float body, float head,
                     float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 1.0, linewidth, antialias);
}

float arrow_angle_60(vec2 texcoord,
                     float body, float head,
                     float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 0.5, linewidth, antialias);
}

float arrow_angle_30(vec2 texcoord,
                     float body, float head,
                     float linewidth, float antialias)
{
    return arrow_angle(texcoord, body, head, 0.25, linewidth, antialias);
}


float arrow_stealth(vec2 texcoord,
                    float body, float head,
                    float linewidth, float antialias)
{
    float w = linewidth/2.0 + antialias;
    vec2 start = -vec2(body/2.0, 0.0);
    vec2 end   = +vec2(body/2.0, 0.0);
    float height = 0.5;

    // Head : 4 lines
    float d1 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end);
    float d2 = line_distance(texcoord, end-head*vec2(+1.0,-height),
                                       end-vec2(3.0*head/4.0,0.0));
    float d3 = line_distance(texcoord, end-head*vec2(+1.0,+height), end);
    float d4 = line_distance(texcoord, end-head*vec2(+1.0,+0.5),
                                       end-vec2(3.0*head/4.0,0.0));

    // Body : 1 segment
    float d5 = segment_distance(texcoord, start, end - vec2(linewidth,0.0));

    return min(d5, max( max(-d1, d3), - max(-d2,d4)));
}
