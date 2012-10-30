PyGLy
=====================

<img src="https://github.com/adamlwgriffiths/PyGLy/raw/master/logo/pygly-300x160.png">

PyGLy is a flexible OpenGL framework that sits ontop of Pyglet.

Design
-------------

   * OpenGL agnostic - Use Legacy (<=2.1) or Core (>=3) profiles.
   * Cross-platform - Actively developed on Windows, Linux and Mac OS-X.
   * Easy to install - Written in pure python and making use of Pyglet for windowing.
   * Modular design - Take almost any part of PyGLy and use it on its own.
   * Loosely coupled framework, not an engine - Don't like an existing class? Don't use it! PyGLy doesn't force any programming method on you.
   * Duck-typing - Replace any class with your own.
   * Full control over rendering process.
   * Uses Pyrr for Maths - NumPy powered Quaternion, Matrix, Vectors, Rays.
   * Liberal BSD licensing - Do what you want!
   * Active development - Being developed for games.

Features
-------------
   * Windowing - Supports multiple windows as per Pyglet.
   * Viewports - Multiple viewports using simple to use wrappers.
   * Optional scene objects - Scene nodes, cameras, render nodes.
   * 3D transform objects - Wraps 3D maths in intuitive objects.
   * GLSL shader support - Helpful error parsing.
   * Sorting - Sort scene to minimise over-draw and to support transparency.
   * Texture - Easily create OpenGL textures using raw data or PIL.
   * View Matrices - Simple wrappers that provide easy manipulation of the view matrix.
   * GL functions - Python wrappers for common tasks.
   * Input - Simple event handlers for digital and analgue events.
   * Cocos2D - Support for rendering PyGLy as a Cocos2D layer (OpenGL Legacy only).

Philosophy
-------------

   * FRAMEWORK, not an engine. Program any way you want.
   * FLEXIBLE, don't force any one method upon the user
   * FULL CONTROL at all times. Full access to rendering, objects, data. No obfuscation. No 'awesome' tricks. Just good, simple code.
   * EASY INSTALLATION. No crazy C++ bindings and complex build procedures.
   * EXPOSE as much functionality as possible. Lower classes are always accessible or usable on their own.
   * LOOSE COUPLING. Code designed with minimal coupling, allowing you to use only what you want.
   * OPTIONAL high level classes. Low level code is always usable. High level API is optional.
   * EXAMPLES of high quality.
   * PYTHON to the core.
   * SPEED in development. Simple and Intuitive code provides convenience functions where it makes sense.
   * DEFINED GOALS. PyGLy aims to provide a high quality, base. PyGLy will never become bloat-ware.
   * PARTNER PROJECTS. PyGLy provides the core of our 3D stack.


Installation
--------------

PyGLy is in the PyPi database and can be installed via pip:
```
pip install pygly
```

PyGLy requires the following software:

   * Python 2(.6?)+
   * Pyglet
   * NumPy
   * Pyrr (https://github.com/adamlwgriffiths/Pyrr)

Source Installation
-------------------

Install PyGLy
```
git clone git@github.com:adamlwgriffiths/PyGLy.git
```

Install Pyrr (a submodule in PyGLy's /contrib directory)
```
cd PyGLy
git submodule init
git submodule update
```

Install PyGLy depedencies:
```
pip install -r requirements.txt
```

Check that it worked!
```
python pygly/examples/legacy/simple/main.py
```


Usage
-----------------------

Check the 'pygly/examples' directory for for some example code.

Development
-----------------------

<img src="http://twistedpairdevelopment.files.wordpress.com/2010/10/twisted_pair-0086.png">

PyGLy is developed by [Twisted Pair Development](http://twistedpairdevelopment.wordpress.com).

Contributions are welcome.

License
---------------

PyGLy is released under the BSD 2-clause license (a very relaxed licence), but it is encouraged that any modifications are submitted back to the master for inclusion.

Created by Adam Griffiths.

Copyright (c) 2012, Twisted Pair Development.
All rights reserved.

twistedpairdevelopment.wordpress.com
@twistedpairdev

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.
