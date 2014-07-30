## Vispy: interactive scientific visualization in Python

Main website: http://vispy.org

<div>
<a href='https://travis-ci.org/vispy/vispy'><img src='https://travis-ci.org/vispy/vispy.png?branch=master' alt='Build Status' /></a> 
<a href='https://coveralls.io/r/vispy/vispy?branch=master'><img src='https://coveralls.io/repos/vispy/vispy/badge.png?branch=master' alt='Coverage Status' /></a> 
</div>


Vispy is a **high-performance interactive 2D/3D data visualization library**. 
Vispy leverages the computational power of modern 
**Graphics Processing Units (GPUs)** through the **OpenGL** library to 
display very large datasets. Applications of Vispy include:

* High-quality interactive scientific plots with tens of millions of points.
* Direct visualization of real-time data.
* Fast interactive visualization of 3D models (meshes, volume rendering).
* OpenGL visualization demos.
* Scientific GUIs with fast, scalable visualization widgets (Qt or IPython notebook with WebGL).

**Important note**. As of today (July 2014), using Vispy requires knowing OpenGL. Within the next few weeks, we will offer higher-level graphical interfaces that allow for the creation of visualizations without any knowledge of OpenGL.


Installation
------------

Vispy runs on Python 2.6+ and Python 3.3+ and depends on Numpy and PyOpenGL.

As Vispy is under heavy development at this time, we highly recommend you to use the development version on Github  (master branch). You need to clone the repository and install Vispy with `python setup.py install`.


About us
--------

The core development team consists of Luke Campagnola, Almar Klein,
Nicolas Rougier, Eric Larson, Cyrille Rossant. Four of us have written our own 
Python visualization toolkit (PyQtGraph, Visvis, Glumpy and Galry), and 
we decided to team-up to create a unique high-performance, high-quality 
interactive visualization library.

* [User mailing list](https://groups.google.com/forum/#!forum/vispy>)
* [Dev mailing list](https://groups.google.com/forum/#!forum/vispy-dev>)
* [Dev chat room](https://gitter.im/vispy/vispy>)
* [Wiki](http://github.com/vispy/vispy/wiki)
* [Gallery](http://vispy.org/gallery.html)
* [Documentation](http://vispy.readthedocs.org)
