Welcome to vispy's documentation!
=================================

Vispy is a **high-performance interactive 2D/3D data visualization
library**. Vispy leverages the computational power of modern **Graphics
Processing Units (GPUs)** through the **OpenGL** library to display very
large datasets.

.. toctree::
   :maxdepth: 1

   index

Overview
========

Vispy is a young library under heavy development at this time. It
targets two categories of users:

1. **Users knowing OpenGL**, or willing to learn OpenGL, who want to
   create beautiful and fast interactive 2D/3D visualizations in Python
   as easily as possible.
2. **Scientists without any knowledge of OpenGL**, who are seeking a
   high-level, high-performance plotting toolkit.

If you're in the first category, you can already start using Vispy.
Vispy offers a Pythonic, NumPy-aware, user-friendly interface for OpenGL
ES 2.0 called **gloo**. You can focus on writing your GLSL code (a GPU 
language) instead of dealing with the complicated OpenGL API - Vispy takes 
care of that automatically for you.

If you're in the second category, we're starting to build experimental
high-level plotting interfaces. Notably, Vispy now ships a very basic
and experimental OpenGL backend for matplotlib.


Getting started
---------------

We are still working on a complete user guide for Vispy. In the meantime, you
can:

  * Check out the `gallery <http://vispy.org/gallery.html>`_
  * Use the ``vispy.plot`` and ``vispy.scene`` interfaces for high-level work
    (WARNING: experimental / developing code)
  * Use the ``vispy.mpl_plot`` experimental OpenGL backend for matplotlib
  * Start learning OpenGL (see below)
  * Write your own visualizations with ``vispy.gloo`` (requires knowing some 
    OpenGL/GLSL)
  

Learning the fundamentals of modern OpenGL
------------------------------------------

Vispy will eventually provide high-level facilities to let scientists create
high-quality, high-performance plots without any knowledge of OpenGL. In the 
meantime, you can learn more about modern OpenGL in the references below.

Even when Vispy is mature enough, knowing OpenGL will still let you write 
entirely custom interactive visualizations that fully leverage the power of
GPUs.

  * `A tutorial about Vispy <http://ipython-books.github.io/featured-06/>`_, by Cyrille Rossant, published in the `IPython Cookbook <http://ipython-books.github.io/>`_
  * `A tutorial about modern OpenGL and Vispy, by Nicolas Rougier <http://www.loria.fr/~rougier/teaching/opengl/>`_
  * A paper on the fundamentals behing Vispy: `Rossant C and Harris KD, Hardware-accelerated interactive data visualization for neuroscience in Python, Frontiers in Neuroinformatics 2013 <http://journal.frontiersin.org/Journal/10.3389/fninf.2013.00036/full>`_
  * A free online book on modern OpenGL (but not Python): `Learning Modern 3D Graphics Programming, by Jason L. McKesson <http://www.arcsynthesis.org/gltut/>`_
  * `A PyOpenGL tutorial <http://cyrille.rossant.net/2d-graphics-rendering-tutorial-with-pyopengl/>`_
  * `A tutorial on OpenGL shaders <http://cyrille.rossant.net/shaders-opengl/>`_


API reference
=============

.. toctree::
   :maxdepth: 2
   
   vispy - Top-level tools <vispy>
   vispy.app - Application, event loops, canvas, backends <app>
   vispy.color - Handling colors <color>
   vispy.geometry - Visualization-related geometry routines <geometry>
   vispy.gloo - User-friendly, Pythonic, object-oriented interface to OpenGL <gloo>
   vispy.io - Data IO <io>
   vispy.mpl_plot - OpenGL backend for matplotlib [experimental] <mpl_plot>
   vispy.plot - Vispy native plotting module <plot>
   vispy.scene - The system underlying the upcoming high-level visualization interfaces [experimental] <scene>
   vispy.util - Miscellaneous utilities <util>
   
   examples
   releasenotes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
