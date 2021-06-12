VisPy: interactive scientific visualization in Python
-----------------------------------------------------

Main website: http://vispy.org

|Build Status| |Coverage Status| |Zenodo Link|

----

VisPy is a **high-performance interactive 2D/3D data visualization
library**. VisPy leverages the computational power of modern **Graphics
Processing Units (GPUs)** through the **OpenGL** library to display very
large datasets. Applications of VisPy include:

-  High-quality interactive scientific plots with millions of points.
-  Direct visualization of real-time data.
-  Fast interactive visualization of 3D models (meshes, volume
   rendering).
-  OpenGL visualization demos.
-  Scientific GUIs with fast, scalable visualization widgets (`Qt <http://www.qt.io>`__ or
   `IPython notebook <http://ipython.org/notebook.html>`__ with WebGL).


Announcements
-------------

- **Release!** Version 0.6.5, September 24, 2020
- **Release!** Version 0.6.4, December 13, 2019
- **Release!** Version 0.6.3, November 27, 2019
- **Release!** Version 0.6.2, November 4, 2019
- **Release!** Version 0.6.1, July 28, 2019
- **Release!** Version 0.6.0, July 11, 2019
- **Release!** Version 0.5.3, March 28, 2018
- **Release!** Version 0.5.2, December 11, 2017
- **Release!** Version 0.5.1, November 4, 2017
- **Release!** Version 0.5, October 24, 2017
- **Release!** Version 0.4, May 22, 2015
- `VisPy tutorial in the IPython Cookbook <https://github.com/ipython-books/cookbook-code/blob/master/featured/06_vispy.ipynb>`__
- **Release!** Version 0.3, August 29, 2014
- **EuroSciPy 2014**: talk at Saturday 30, and sprint at Sunday 31, August 2014
- `Article in Linux Magazine, French Edition <https://github.com/vispy/linuxmag-article>`__, July 2014
- **GSoC 2014**: `two GSoC students are currently working on VisPy under the PSF umbrella <https://github.com/vispy/vispy/wiki/Project.%20GSoC-2014>`__
- **Release!**, Version 0.2.1 04-11-2013
- **Presentation at BI forum**, Budapest, 6 November 2013
- **Presentation at Euroscipy**, Belgium, August 2013
- **EuroSciPy Sprint**, Belgium, August 2013
- **Release!** Version 0.1.0 14-08-2013


Using VisPy
-----------

VisPy is a young library under heavy development at this time. It
targets two categories of users:

1. **Users knowing OpenGL**, or willing to learn OpenGL, who want to
   create beautiful and fast interactive 2D/3D visualizations in Python
   as easily as possible.
2. **Scientists without any knowledge of OpenGL**, who are seeking a
   high-level, high-performance plotting toolkit.

If you're in the first category, you can already start using VisPy.
VisPy offers a Pythonic, NumPy-aware, user-friendly interface for OpenGL
ES 2.0 called **gloo**. You can focus on writing your GLSL code instead
of dealing with the complicated OpenGL API - VisPy takes care of that
automatically for you.

If you're in the second category, we're starting to build experimental
high-level plotting interfaces. Notably, VisPy now ships a very basic
and experimental OpenGL backend for matplotlib.


Installation
------------

Please follow the detailed
`installation instructions <http://vispy.org/installation.html>`_
on the VisPy website.

Structure of VisPy
------------------

Currently, the main subpackages are:

-  **app**: integrates an event system and offers a unified interface on
   top of many window backends (Qt4, wx, glfw, IPython notebook
   with/without WebGL, and others). Relatively stable API.
-  **gloo**: a Pythonic, object-oriented interface to OpenGL. Relatively
   stable API.
-  **scene**: this is the system underlying our upcoming high level
   visualization interfaces. Under heavy development and still
   experimental, it contains several modules.

   -  **Visuals** are graphical abstractions representing 2D shapes, 3D
      meshes, text, etc.
   -  **Transforms** implement 2D/3D transformations implemented on both
      CPU and GPU.
   -  **Shaders** implements a shader composition system for plumbing
      together snippets of GLSL code.
   -  The **scene graph** tracks all objects within a transformation
      graph.
-  **plot**: high-level plotting interfaces.

The API of all public interfaces are subject to change in the future,
although **app** and **gloo** are *relatively* stable at this point.


Genesis
-------

VisPy began when four developers with their own visualization libraries
decided to team up:
`Luke Campagnola <http://luke.campagnola.me/>`__ with `PyQtGraph <http://www.pyqtgraph.org/>`__,
`Almar Klein <http://www.almarklein.org/>`__ with `Visvis <https://github.com/almarklein/visvis>`__,
`Cyrille Rossant <http://cyrille.rossant.net>`__ with `Galry <https://github.com/rossant/galry>`__,
`Nicolas Rougier <http://www.loria.fr/~rougier/index.html>`__ with `Glumpy <https://github.com/rougier/Glumpy>`__.

Now VisPy looks to build on the expertise of these developers and the
broader open-source community to build a high-performance OpenGL library.

----

External links
--------------

-  `User mailing
   list <https://groups.google.com/forum/#!forum/vispy>`__
-  `Dev mailing
   list <https://groups.google.com/forum/#!forum/vispy-dev>`__
-  `Dev chat room <https://gitter.im/vispy/vispy>`__
-  `Wiki <http://github.com/vispy/vispy/wiki>`__
-  `Gallery <http://vispy.org/gallery.html>`__
-  `Documentation <http://vispy.readthedocs.org>`__

.. |Build Status| image:: https://github.com/vispy/vispy/workflows/CI/badge.svg
   :target: https://github.com/vispy/vispy/actions
.. |Coverage Status| image:: https://img.shields.io/coveralls/vispy/vispy/main.svg
   :target: https://coveralls.io/r/vispy/vispy?branch=main
.. |Zenodo Link| image:: https://zenodo.org/badge/5822/vispy/vispy.svg
   :target: http://dx.doi.org/10.5281/zenodo.17869
