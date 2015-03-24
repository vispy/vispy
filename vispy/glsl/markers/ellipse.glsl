// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// -----------------------------------------------------------------------------

// --- ellipse
// Created by Inigo Quilez - iq/2013
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
float marker_ellipse(vec2 P, float size)
{
    // Alternate version (approximation)
    float a = 1.0;
    float b = 2.0;
    float r = 0.5*size;
    float f = length( P*vec2(a,b) );
    f = length( P*vec2(a,b) );
    f = f*(f-r)/length( P*vec2(a*a,b*b) );
    return f;

/*
    vec2 ab = vec2(size/3.0, size/2.0);
    vec2 p = abs( P );
    if( p.x > p.y ){
        p = p.yx;
        ab = ab.yx;
    }
    float l = ab.y*ab.y - ab.x*ab.x;
    float m = ab.x*p.x/l;
    float n = ab.y*p.y/l;
    float m2 = m*m;
    float n2 = n*n;

    float c = (m2 + n2 - 1.0)/3.0;
    float c3 = c*c*c;

    float q = c3 + m2*n2*2.0;
    float d = c3 + m2*n2;
    float g = m + m*n2;

    float co;

    if(d < 0.0)
    {
        float p = acos(q/c3)/3.0;
        float s = cos(p);
        float t = sin(p)*sqrt(3.0);
        float rx = sqrt( -c*(s + t + 2.0) + m2 );
        float ry = sqrt( -c*(s - t + 2.0) + m2 );
        co = ( ry + sign(l)*rx + abs(g)/(rx*ry) - m)/2.0;
    }
    else
    {
        float h = 2.0*m*n*sqrt( d );
        float s = sign(q+h)*pow( abs(q+h), 1.0/3.0 );
        float u = sign(q-h)*pow( abs(q-h), 1.0/3.0 );
        float rx = -s - u - c*4.0 + 2.0*m2;
        float ry = (s - u)*sqrt(3.0);
        float rm = sqrt( rx*rx + ry*ry );
        float p = ry/sqrt(rm-rx);
        co = (p + 2.0*g/rm - m)/2.0;
    }

    float si = sqrt(1.0 - co*co);
    vec2 closestPoint = vec2(ab.x*co, ab.y*si);
    return length(closestPoint - p ) * sign(p.y-closestPoint.y);
*/
}
