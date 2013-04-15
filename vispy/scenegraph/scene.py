"""
The job of the scene object is to:
 - initialize GL matrix to fit backend widget
 - manage a hierarchy of visualization objects
 - coordinate rendering all objects in the correct order
 - accept UI events from the backend and distribute events to the individual objects
 - handle rendering sub-regions of the scene if possible

The scene should _not_ be responsible for cameras--this should be handled by primitives.box

The scene should _not_ be required--should be possible to make use of primitives directly
"""
