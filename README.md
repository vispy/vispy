## Vispy: interactive scientific visualization in Python

Main website: http://vispy.org

<div>
<a href='https://travis-ci.org/vispy/vispy'><img src='https://travis-ci.org/vispy/vispy.png?branch=master' alt='Build Status' /></a> 
<a href='https://coveralls.io/r/vispy/vispy?branch=master'><img src='https://coveralls.io/repos/vispy/vispy/badge.png?branch=master' alt='Coverage Status' /></a> 
</div>


Vispy is a **high-performance interactive 2D/3D data visualization library**. Vispy leverages the computational power of modern **Graphics Processing Units (GPUs)** through the **OpenGL** library to display very large datasets. Applications of Vispy include:

* High-quality interactive scientific plots with millions of points.
* Direct visualization of real-time data.
* Fast interactive visualization of 3D models (meshes, volume rendering).
* OpenGL visualization demos.
* Scientific GUIs with fast, scalable visualization widgets (Qt or IPython notebook with WebGL).


Using Vispy
-----------

Vispy is a young library under heavy development at this time. It targets two categories of users:

1. **Users knowing OpenGL**, or willing to learn OpenGL, who want to create beautiful and fast interactive 2D/3D visualizations in Python as easily as possible.
2. **Scientists without any knowledge of OpenGL**, who are seeking a high-level, high-performance plotting toolkit.

If you're in the first category, you can already start using Vispy. Vispy offers a Pythonic, NumPy-aware, user-friendly interface for OpenGL ES 2.0 called **gloo**. You can focus on writing your GLSL code instead of dealing with the complicated OpenGL API - Vispy takes care of that automatically for you.

If you're in the second category, we're starting to build experimental high-level plotting interfaces. Notably, Vispy now ships a very basic and experimental OpenGL backend for matplotlib.


Installation
------------

Vispy runs on Python 2.6+ and Python 3.3+ and depends on NumPy. You also need a backend (PyQt4/PySide, glfw, GLUT, pyglet, or SDL).

As Vispy is under heavy development at this time, we highly recommend you to use the development version on Github  (master branch). You need to clone the repository and install Vispy with `python setup.py install`.


Structure of Vispy
------------------

Currently, the main subpackages are:

* **app**: integrates an event processing system and offers a unified interface on top of many window backends (qt, GLUT, glfw, and others). Relatively stable API.
* **gloo**: a Pythonic, object-oriented interface to OpenGL. Relatively stable API.
* **mpl_plot**: an OpenGL backend for matplotlib. Experimental.
* **scene**: the core of Vispy implements four systems for organizing graphical objects within the scene. Under heavy development and still experimental.
    * **Visuals** are graphical abstractions representing 2D shapes, 3D meshes, text, etc.
    * **Transforms** implement 2D/3D transformations implemented on both CPU and GPU.
    * **Shaders** implements a shader composition system for plumbing together snippets of GLSL code.
    * The **scene graph** tracks all objects within a transformation graph.

The API of all public interfaces are subject to change in the future, although **app** and **gloo** are *relatively* stable at this point.


About us
--------

The core development team consists of:

* [Luke Campagnola](http://luke.campagnola.me/)
* [Almar Klein](http://www.almarklein.org/)
* Eric Larson
* [Cyrille Rossant](http://cyrille.rossant.net)
* [Nicolas Rougier](http://www.loria.fr/~rougier/index.html)

Four of us have written our own Python visualization toolkit ([PyQtGraph](http://www.pyqtgraph.org/) by LC, [Visvis](https://code.google.com/p/visvis/) by AK, [Glumpy](https://github.com/rougier/Glumpy) by NR, and [Galry](https://github.com/rossant/galry) by CR), and we decided to team up to create a unique high-performance, high-quality interactive visualization library.


External links
--------------

* [User mailing list](https://groups.google.com/forum/#!forum/vispy>)
* [Dev mailing list](https://groups.google.com/forum/#!forum/vispy-dev>)
* [Dev chat room](https://gitter.im/vispy/vispy>)
* [Wiki](http://github.com/vispy/vispy/wiki)
* [Gallery](http://vispy.org/gallery.html)
* [Documentation](http://vispy.readthedocs.org)
