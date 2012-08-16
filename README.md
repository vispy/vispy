PyGLy
=====================

PyGLy is a flexible OpenGL framework that sits ontop of Pyglet.

PyGLy's core values are the following:

   * FRAMEWORK, not an engine. Program any way you want.
   * FLEXIBLE, don't force any one method upon the user
   * FULL CONTROL at all times. Full access to rendering, objects, data. No obfuscation. No 'awesome' tricks. Just good, simple code.
   * EASY INSTALLATION. No crazy C++ bindings and complex build procedures.
   * EXPOSE as much functionality as possible. Lower classes are always accessible or usable on their own.
   * LOOSE COUPLING. Code designed to be reused in various situations.
   * OPTIONAL high level classes. Low level code is always usable. High level API is optional.
   * EXAMPLES of high quality.
   * PYTHON to the core.
   * SPEED in development. Provide convenience functions where it makes sense.

Features
-------------

   * Cross-platform - actively developed on Windows and OS-X.
   * Easy to install - Written in pure python and making use of Pyglet for windowing.
   * Modular design - Take almost any part of PyGLy and use it on its own.
   * Framework design, not an engine - Don't like an existing class? Don't use it!
   * Multiple Window and viewport support.
   * Multiple parallel scene graphs.
   * Full control over rendering process.
   * Maths helper classes - Quaternion, Matrix, Vectors, Rays.
   * NumPy - Translate vectors and matrices en-masse.
   * Mesh loading support - MD2, OBJ.
   * Duck-typing - Replace any class with your own. Just meet the minimal inter-object contracts.
   * Liberal BSD licensing - Do what you want!
   * Active development - Being developed for games.


Installation
--------------

PyGLy requires the following software:

   * Python 2(.6?)+
   * Pyglet
   * NumPy
   * Pyrr (https://github.com/adamlwgriffiths/Pyrr)


Install Pyrr
```
git submodule init
git submodule update
```

Install PyGLy depedencies:
```
pip install -r requirements.txt
```

Windows users can stop there.

Mac OS-X users need to continue to install more dependencies:
```
pip install -r requirements-osx.txt
```


Usage
-----------------------

Check the 'examples' directory for for some example code.

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
