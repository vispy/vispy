Getting Started
===============

VisPy strives to provide an easy path for users to make fast interactive
visualizations. To serve as many users as possible VisPy provides different
interfaces for differing levels of experience. While one interface may be
enough to build a simple visualization, knowing all the interfaces can provide
the most flexibility for fully customizing your visualization.

The below pages are meant to provide an introduction to these interfaces and
help guide you into what interface might be best for your experience and the
final visualization you are looking to achieve. Additionally, the
:doc:`../gallery/index` can be used for inspiration. Further low-level details can
be found in the :doc:`API documentation <../api/modules>` and existing
examples.

VisPy targets two primary categories of users:

1. **Users knowing OpenGL**, or willing to learn OpenGL, who want to
   create beautiful and fast interactive 2D/3D visualizations in Python
   as easily as possible. Users in this category can write their own
   visualizations with :mod:`vispy.gloo` (requires knowing OpenGL/GLSL).
   Another option with VisPy development is to encapsulate gloo-based
   visualizations into re-usable `Visual` classes. The below pages will
   provide an introduction of these interfaces.

.. toctree::
  :maxdepth: 1

  modern-gl
  Gloo <gloo>
  Visuals <visuals>

2. **Scientists without any knowledge of OpenGL**, who are seeking a
   high-level, high-performance plotting toolkit. Use the :mod:`vispy.plot`
   and :mod:`vispy.scene` interfaces for high-level work. The below pages
   provide an introduction into these interfaces.

.. toctree::
  :maxdepth: 1

  Scene <scene>
  Plotting <plot>

