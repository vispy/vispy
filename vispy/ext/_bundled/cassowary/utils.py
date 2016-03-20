from __future__ import print_function, unicode_literals, absolute_import, division


EPSILON = 1e-8

REQUIRED = 1001001000
STRONG = 1000000
MEDIUM = 1000
WEAK = 1


def approx_equal(a, b, epsilon=EPSILON):
    "A comparison mechanism for floats"
    return abs(a - b) < epsilon


def repr_strength(strength):
    """Convert a numerical strength constant into a human-readable value.

    We could wrap this up in an enum, but enums aren't available in Py2;
    we could use a utility class, but we really don't need the extra
    implementation weight. In practice, this repr is only used for debug
    purposes during development.
    """
    return {
        REQUIRED: 'Required',
        STRONG: 'Strong',
        MEDIUM: 'Medium',
        WEAK: 'Weak'
    }[strength]
