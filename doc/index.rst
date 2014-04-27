==============================================
Interactive scientific visualization in Python
==============================================

`Vispy`_ is an `OpenGL`_-based interactive visualization library in Python. Its
goal is to make it easy to create beautiful and fast dynamic visualizations.

.. _Vispy: http://vispy.org/
.. _OpenGL: http://www.opengl.org

Vispy will eventually offer graphical APIs at multiple levels, including a
matplotlib-like scientific plotting library. Currently, only the lowest-level
API is implemented: it brings an easy-to-use Pythonic object-oriented interface
to OpenGL. This layer requires you to have basic knowledge of modern OpenGL
(notably the OpenGL shading language, GLSL).

For this reason, Vispy is not yet suitable for the general scientist, but it
will be in the future (in several months at the very least). We are currently
working on higher level layers. They will hide most OpenGL concepts and let you
create beautiful visualizations in a few lines of code. Stay tuned!

The main documentation for the site is organized into a couple sections:

* :ref:`user-docs`
* :ref:`dev-docs`
* :ref:`tech-docs`


About us
========

The core development team consists of Luke Campagnola, Almar Klein, Nicolas
Rougier, Cyrille Rossant. We have each written our own Python visualization
toolkit (`PyQtGraph <http://pyqtgraph.org>`_, `Visvis
<https://code.google.com/p/visvis/>`_, `Glumpy
<https://code.google.com/p/glumpy/>`_ and `Galry
<https://github.com/rossant/galry>`_, respectively), and decided to
team-up. Eric Larson joined us later and is now a core contributor as well.

Vispy will eventually replace all of our visualization libraries, so you can
expect vispy to have all the features of our respective toolkits combined, and
more.


.. _user-docs:

User Documentation
==================

.. toctree::
    :maxdepth: 1

    user-quickstart
    user-install
    user-howto
    user-faq
    user-support
    user-notes


.. _dev-docs:

Developer Documentation
=======================

.. toctree::
    :maxdepth: 2

    dev-install
    dev-modern-gl
    dev-api

.. _tech-docs:

Technical Documentation
=======================

.. toctree::
    :maxdepth: 2

    tech-publications
    tech-antialiasing





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
