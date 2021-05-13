# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Define constants for keys.

Each key constant is defined as a Key object, which allows comparison with
strings (e.g. 'A', 'Escape', 'Shift'). This enables handling of key events
without using the key constants explicitly (e.g. ``if ev.key == 'Left':``).

In addition, key objects that represent characters can be matched to
the integer ordinal (e.g. 32 for space, 65 for A). This behavior is mainly
intended as a compatibility measure.

"""


class Key(object):
    """Represent the identity of a certain key.

    This represents one or more names that the key in question is known by.

    A Key object can be compared to one of its string names (case
    insensitive), to the integer ordinal of the key (only for keys that
    represent characters), and to another Key instance.
    """

    def __init__(self, *names):
        self._names = names
        self._names_upper = tuple([v.upper() for v in names])

    @property
    def name(self):
        """The primary name of the key."""
        return self._names[0]

    def __hash__(self):
        return self._names[0].__hash__()

    def __repr__(self):
        return "<Key %s>" % ', '.join([repr(v) for v in self._names])

    def __eq__(self, other):
        if isinstance(other, str):
            return other.upper() in self._names_upper
        elif isinstance(other, Key):
            return self._names[0] == other
        elif isinstance(other, int):
            return other in [ord(v) for v in self._names_upper if len(v) == 1]
        elif other is None:
            return False
        else:
            raise ValueError('Key can only be compared to str, int and Key.')


SHIFT = Key('Shift')
CONTROL = Key('Control')
ALT = Key('Alt')
META = Key('Meta')  # That Mac thingy

UP = Key('Up')
DOWN = Key('Down')
LEFT = Key('Left')
RIGHT = Key('Right')
PAGEUP = Key('PageUp')
PAGEDOWN = Key('PageDown')

INSERT = Key('Insert')
DELETE = Key('Delete')
HOME = Key('Home')
END = Key('End')

ESCAPE = Key('Escape')
BACKSPACE = Key('Backspace')

F1 = Key('F1')
F2 = Key('F2')
F3 = Key('F3')
F4 = Key('F4')
F5 = Key('F5')
F6 = Key('F6')
F7 = Key('F7')
F8 = Key('F8')
F9 = Key('F9')
F10 = Key('F10')
F11 = Key('F11')
F12 = Key('F12')

SPACE = Key('Space', ' ')
ENTER = Key('Enter', 'Return', '\n')
TAB = Key('Tab', '\t')
