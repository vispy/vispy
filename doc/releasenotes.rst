=============
Release notes
=============

**Vispy 0.2.1**

Small fix in the setup script. The buf prevented pip from working.


**Vispy 0.2**

In this release we focussed on improving and finalizing the object
oriented OpenGL interface ``vispy.gloo``. Some major (backward
incompatible) changes were done. However, from this release we consider
the ``vispy.gloo`` package relatively stable and we try to minimize
backward incompatibilities.

Changes in more detail:

  * ``vispy.oogl`` is renamed to ``vispy.gloo``
  * ``vispy.gl`` is moved to ``vispy.gloo.gl`` since most users will
    use gloo to interface with OpenGL.
  * Improved (and thus changed) several parts of the gloo API.
  * Some parts of gloo were refactored and should be more robust.
  * Much better coverage of the test suite.
  * Compatibility with Python 2.6 (Jerome Kieffer)
  * More examples and a gallery on the website to show them off. 


**Vispy 0.1.0**

First release. We have an initial version of the object oriented interface
to OpenGL, called `vispy.oogl`.
