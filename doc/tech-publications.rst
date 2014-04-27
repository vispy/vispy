================
Published papers
================

Hardware-accelerated interactive data visualization for neuroscience in Python
==============================================================================
**C. Rossant and K.D. Harris, Frontiers in Neuroinformatics, 7.36, (2013)**


**Abstract** Large datasets are becoming more and more common in science,
particularly in neuroscience where experimental techniques are rapidly
evolving. Obtaining interpretable results from raw data can sometimes be done
automatically; however, there are numerous situations where there is a need, at
all processing stages, to visualize the data in an interactive way. This
enables the scientist to gain intuition, discover unexpected patterns, and find
guidance about subsequent analysis steps. Existing visualization tools mostly
focus on static publication-quality figures and do not support interactive
visualization of large datasets. While working on Python software for
visualization of neurophysiological data, we developed techniques to leverage
the computational power of modern graphics cards for high-performance
interactive data visualization. We were able to achieve very high performance
despite the interpreted and dynamic nature of Python, by using
state-of-the-art, fast libraries such as NumPy, PyOpenGL, and PyTables. We
present applications of these methods to visualization of neurophysiological
data. We believe our tools will be useful in a broad range of domains, in
neuroscience and beyond, where there is an increasing need for scalable and
fast interactive visualization.

**Download**: http://www.frontiersin.org/Journal/10.3389/fninf.2013.00036/full


Shader-based Antialiased Dashed Stroked Polylines
=================================================
**N.P. Rougier. Journal of Computer Graphics Techniques, 2.2 (2013)**

**Abstract** Dashed stroked paths are a widely-used feature found in the vast
majority of vector-drawing software and libraries. They enable, for example,
the highlighting of a given path, such as the current selection, in drawing
software or distinguishing curves, in the case of a scientific plotting
package. This paper introduces a shader-based method for rendering arbitrary
dash patterns along any continuous polyline (smooth or broken). The proposed
method does not tessellate individual dash patterns and allows for fast and
nearly accurate rendering of any user-defined dash pattern and caps. Benchmarks
indicate a slowdown ratio between 1.1 and 2.1 with an increased memory
consumption between 3 and 6. Furthermore, the method can be used for solid
thick polylines with correct caps and joins with only a slowdown factor of 1.1.

**Download**: http://jcgt.org/published/0002/02/08/


Higher Quality 2D Text Rendering
================================
**N.P. Rougier. Journal of Computer Graphics Techniques, 2.1 (2013)**

**Abstract** Even though text is pervasive in most 3D applications, there is
surprisingly no native support for text rendering in OpenGL. To cope with this
absence, Mark Kilgard introduced the use of texture fonts [Kilgard 1997]. This
technique is well known and widely used and ensures both good performances and
a decent quality in most situations. However, the quality may degrade strongly
in orthographic mode (screen space) due to pixelation effects at large sizes
and to legibility problems at small sizes due to incorrect hinting and
positioning of glyphs. In this paper, we consider font-texture rendering to
develop methods to ensure the highest quality in orthographic mode. The method
used allows for both the accurate render- ing and positioning of any glyph on
the screen. While the method is compatible with complex shaping and/or layout
(e.g., the Arabic alphabet), these specific cases are not studied in this
article.

**Download**: http://jcgt.org/published/0002/01/04/


Conferences slides
==================

* `Vispy, a future tool for interactive visualization <https://github.com/vispy/static/raw/master/vispy-biforum-2013.pdf>`_ - Talk at Budapest BI forum 2013

* `Vispy, a modern and interactive visualization framework <https://github.com/vispy/static/raw/master/vispy-euroscipy-2013.pdf>`_ - Talk at EuroScipy 2013
