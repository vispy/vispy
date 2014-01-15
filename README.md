## Vispy: interactive scientific visualization in Python

Main website: http://vispy.org

<div>
<a href='https://travis-ci.org/vispy/vispy'><img src='https://travis-ci.org/vispy/vispy.png?branch=master' alt='Build Status' /></a> 
<a href='https://coveralls.io/r/vispy/vispy?branch=master'><img src='https://coveralls.io/repos/vispy/vispy/badge.png?branch=master' alt='Coverage Status' /></a> 
<a href='https://bitdeli.com/free'><img src='https://d2weczhvl823v0.cloudfront.net/vispy/vispy/trend.png' alt='Bitdeli Badge' /></a> 
</div>

### Description

Vispy is an OpenGL-based interactive visualization library in Python. Its goal is to make it easy to create beautiful and fast dynamic visualizations. For example, scientific plotting of tens of millions of points, interacting with complex polygonial models, and (dynamic) volume rendering. All thanks to the graphics card’s hardware acceleration.

### Status

Vispy will eventually offer graphical APIs at multiple levels, including a matplotlib-like scientific plotting library. Currently, only the lowest-level API is implemented: it brings an easy-to-use Pythonic object-oriented interface to OpenGL. This layer requires you to have basic knowledge of modern OpenGL (notably the OpenGL shading language, GLSL).

For this reason, Vispy is not yet suitable for the general scientist, but it will be in the future (in several months at the very least). We are currently working on higher level layers. They will hide most OpenGL concepts and let you create beautiful visualizations in a few lines of code. Stay tuned!


### Installation

Vispy runs on Python 2.6 and higher, including Python 3. Vispy depends on Numpy and PyOpenGL.
Since Vispy is pure Python, installation is easy, for instance via `pip install vispy`. 


### About us

The core development team consists of Luke Campagnola, Almar Klein, 
Nicolas Rougier and Cyrille Rossant. We have each written our own 
Python visualization toolkit (PyQtGraph, Visvis, Glumpy and Galry, 
respectively), and decided to team-up.
Vispy will eventually replace all of our visualization libraries, so 
you can expect vispy to have all the features of our respective 
toolkits combined, and more.


### Contributions

You want to help out? Fork our repo and come up with a pull request! Or discuss new ideas in the mailing list.


### More information

  * Have a look at the code at http://github.com/vispy/vispy
  * Our mailing list is at: https://groups.google.com/d/forum/vispy
  * API documentation is at http://vispy.readthedocs.org
  * Visit our gallery for examples: http://vispy.org/gallery.html
  * View the [wiki](http://github.com/vispy/vispy/wiki) for more information about this project.

