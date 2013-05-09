""" Define constants for keys.
These are taken from Qt, but this is arbitrary and should not be relied on.
"""

# Keys that are also modifiers
# Note that Qt and PyGlet use separate constants for shift-as-a-key and
# shift-as-a-modifier. Is this useful?
SHIFT = 16777248
CONTROL = 16777249  # Command key on Mac
ALT = 16777251

# Common keys
LEFT = 16777234
UP = 16777235
RIGHT = 16777236
DOWN = 16777237
PAGEUP = 16777238
PAGEDOWN = 16777239
ESCAPE = 16777216
DELETE = 16777223
BACKSPACE = 16777219

# todo: Function keys
# F1 =
# F2 = 
# etc.

# A few easy ones for convenience
SPACE = ord(' ')
ENTER = ord('\n')  # Note that Qt has diffent constants for Enter and Return
