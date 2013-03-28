"""
Base class for visualization objects. Anything that can be displayed or placed in a scenegraph hierarchy will ultimately inherit from this class.

Should define:
 - methods for drawing to OpenGL based on version
 - methods for drawing to SVG / EPS, etc.
 - set of matrix transformations:
      - each visualization object should have at least two transformation matrices
          - one (or more) 'external' matrix is to allow the object to be transformed by the user
          - one 'internal' matrix allows the object to internally define its own coordinate system
      - total transform is simply the product of all matrices in the list
        (however objects should be free to redefine this behavior where appropriate) 
 - object hierarchy information--parent and children
 - basic cascading stylesheet system (see util/stylesheet)
 - basic user interaction - mouse, keyboard, tablet, focus, etc.
      (but note that a scenegraph would be required to deliver events to each object)
"""
