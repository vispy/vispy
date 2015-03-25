// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

/* ---------------------------------------------------------

   Project a point p onto a line (p0,p1) and return linear position u such that
   p' = p0 + u*(p1-p0)

   Parameters:
   -----------

   p0, p1: Points describing the line
   p: Point to be projected

   Return:
   -------
   Linear position of p onto (p0,p1)

   --------------------------------------------------------- */
float point_to_line_projection(vec2 p0, vec2 p1, vec2 p)
{
    // Projection p' of p such that p' = p0 + u*(p1-p0)
    // Then  u *= lenght(p1-p0)
    vec2 v = p1 - p0;
    float l = length(v);
    return ((p.x-p0.x)*v.x + (p.y-p0.y)*v.y) / l;
}
