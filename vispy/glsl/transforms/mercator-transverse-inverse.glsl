// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Constants
// ------------------------------------
const float k0 = 0.75;
const float a  = 1.00;


// Helper functions
// ------------------------------------
float cosh(float x) { return 0.5 * (exp(x)+exp(-x)); }
float sinh(float x) { return 0.5 * (exp(x)-exp(-x)); }


/* ---------------------------------------------------------
   Inverse Lambert azimuthal equal-area projection
   -> http://en.wikipedia.org/wiki/Transverse_Mercator_projection

   Parameters:
   -----------

   position : 2d position in cartesian coordinates

   Return:
   -------
   2d position in (longitude,latitiude) coordinates

   --------------------------------------------------------- */

vec2 transform_inverse(vec2 P)
{
    float x = P.x;
    float y = P.y;
    float lambda = atan(sinh(x/(k0*a)),cos(y/(k0*a)));
    float phi    = asin(sin(y/(k0*a))/cosh(x/(k0*a)));
    return vec2(lambda,phi);
}
