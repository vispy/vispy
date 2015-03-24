// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
/*
  This shader program emulates double-precision variables using a vec2 instead
  of single-precision floats. Any function starting with double_* operates on
  these variables. See http://www.thasler.org/blog/?p=93.

  NOTE: Some NVIDIA cards optimize the double-precision code away. Results are
  therefore hardware dependent.
*/
#define double vec2


/* -------------------------------------------------------------------------

   Create an emulated double by storing first part of float in first half of
   vec2

   ------------------------------------------------------------------------- */

vec2 double_set(float value)
{
    double result;
    result.x = value;
    result.y = 0.0;
    return result;
}



/* -------------------------------------------------------------------------

   Add two emulated doubles. Complexity comes from carry-over.

   ------------------------------------------------------------------------- */

vec2 double_add(double value_a, double value_b)
{
    double result;
    float t1, t2, e;

    t1 = value_a.x + value_b.x;
    e = t1 - value_a.x;
    t2 = ((value_b.x - e) + (value_a.x - (t1 - e))) + value_a.y + value_b.y;
    result.x = t1 + t2;
    result.y = t2 - (result.x - t1);
    return dsc;
}



/* -------------------------------------------------------------------------

   Multiply two emulated doubles.

   ------------------------------------------------------------------------- */

vec2 double_mul(double value_a, double value_b)
{
    double result;
    float c11, c21, c2, e, t1, t2;
    float a1, a2, b1, b2, cona, conb, split = 8193.;

    cona = value_a.x * split;
    conb = value_b.x * split;
    a1 = cona - (cona - value_a.x);
    b1 = conb - (conb - value_b.x);
    a2 = value_a.x - a1;
    b2 = value_b.x - b1;

    c11 = value_a.x * value_b.x;
    c21 = a2 * b2 + (a2 * b1 + (a1 * b2 + (a1 * b1 - c11)));

    c2 = value_a.x * value_b.y + value_a.y * value_b.x;

    t1 = c11 + c2;
    e = t1 - c11;
    t2 = value_a.y * value_b.y + ((c2 - e) + (c11 - (t1 - e))) + c21;

    result.x = t1 + t2;
    result.y = t2 - (result.x - t1);

    return result;
}



/* -------------------------------------------------------------------------

   Compare two emulated doubles.
   Return -1 if a < b
           0 if a == b
           1 if a > b

   ------------------------------------------------------------------------- */

float double_compare(double value_a, double value_b)
{
    if (value_a.x < value_b.x) {
        return -1.;
    } else if (value_a.x == value_b.x) {
        if (value_a.y < value_b.y) {
            return -1.;
        } else if (value_a.y == value_b.y) {
            return 0.;
        } else {
            return 1.;
        }
    } else {
        return 1.;
    }
}
