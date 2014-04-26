.. vispy documentation master file, created by
   sphinx-quickstart on Sat May  4 16:52:02 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Interactive scientific visualization in Python
===============================================================================


Vispy is an OpenGL-based interactive visualization library in Python. Its goal
is to make it easy to create beautiful and fast dynamic visualizations. For
example, scientific plotting of tens of millions of points, interacting with
complex polygonial models, and (dynamic) volume rendering. All thanks to the
graphics card’s hardware acceleration.


Status
-------------------------------------------------------------------------------

Vispy will eventually offer graphical APIs at multiple levels, including a
matplotlib-like scientific plotting library. Currently, only the lowest-level
API is implemented: it brings an easy-to-use Pythonic object-oriented interface
to OpenGL. This layer requires you to have basic knowledge of modern OpenGL
(notably the OpenGL shading language, GLSL).

For this reason, Vispy is not yet suitable for the general scientist, but it
will be in the future (in several months at the very least). We are currently
working on higher level layers. They will hide most OpenGL concepts and let you
create beautiful visualizations in a few lines of code. Stay tuned!


About us
-------------------------------------------------------------------------------

The core development team consists of Luke Campagnola, Almar Klein, Nicolas
Rougier, Cyrille Rossant. We have each written our own Python visualization
toolkit (`PyQtGraph <http://pyqtgraph.org>`_, `Visvis
<https://code.google.com/p/visvis/>`_, `Glumpy
<https://code.google.com/p/glumpy/>`_ and `Galry
<https://github.com/rossant/galry>`_, respectively), and decided to
team-up. Eric Larson joined us later and is now a core contributor.

Vispy will eventually replace all of our visualization libraries, so you can
expect vispy to have all the features of our respective toolkits combined, and
more.


.. toctree::
   :maxdepth: 2
   :hidden:

   installation.rst
   vispy.app - Application API <app>
   vispy.gloo - object oriented GL API <gloo>
   vispy.util - Utilities <util>

   examples
   releasenotes



More information
-------------------------------------------------------------------------------

  * Code repository at http://github.com/vispy/vispy
  * Mailing list is at https://groups.google.com/d/forum/vispy
  * API documentation at http://vispy.readthedocs.org
  * Gallery of examples at http://vispy.org/gallery.html




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
