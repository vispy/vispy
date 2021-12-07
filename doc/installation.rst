============
Installation
============

Package requirements
====================

The only mandatory requirement for VisPy is the `numpy <http://numpy.org>`_
package.

Backend requirements
====================

VisPy requires at least one toolkit for opening a window and creates an OpenGL
context. This can be done using any one of the following.

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

   * - Backend
     - Status
     - Dependencies
   * - pyqt4
     - Stable
     - pyqt4
   * - pyqt5
     - Stable
     - pyqt5
   * - pyqt6
     - Stable
     - pyqt6
   * - pyside
     - Stable
     - pyside
   * - pyside2
     - Stable
     - pyside2
   * - pyside6
     - Stable
     - pyside6
   * - glfw
     - Stable
     - glfw (python)
   * - sdl2
     - Stable
     - pysdl2 (pysdl2-dll recommended for MacOS/Windows)
   * - wx
     - Stable
     - wxPython
   * - pyglet
     - Stable
     - pyglet
   * - tkinter
     - Experimental
     - pyopengltk

You can also use a Jupyter notebook with visualizations appearing inline with the ``jupyter_rfb`` backend (requires ``jupyter_rfb`` package).

.. warning::

   You only need to have one of these packages, no need to install them all!

Optional dependencies
=====================

VisPy has various optional dependencies to support features that may not be relevant for all users. The below is a list of dependencies that you may want to install to use the functionality mentioned.

* **pillow**: Pillow (imported as PIL) is used to read image files. Some VisPy examples will use Pillow to load the image data that will then be shown by VisPy.
* **triangle**: The `Triangle C package <https://www.cs.cmu.edu/~quake/triangle.html>`_ is used via it's `triangle python <https://github.com/drufat/triangle>`_ bindings. Please acknowledge and adhere to the licensing terms of both packages. Within VisPy `triangle`, if installed, is used to calculate a constrained Delaunay triangulation for `PolygonCollections`.

Hardware requirements
=====================

VisPy makes heavy use of the graphic card installed on your system. More
precisely, VisPy uses the Graphical Processing Unit (GPU) through
shaders. VisPy thus requires a fairly recent video card (~ less than 12 years
old) as well as an up-to-date video driver such that vispy can access the
programmable pipeline (as opposed to the fixed pipeline).

To get information on your system, you can type:

.. code-block:: python

   >>> print(vispy.sys_info())

The results of the above command and is long list of information related to
your system and video driver. The OpenGL version must be at least 2.1.

.. note::

    On linux systems the `xrandr` command is used to determine the screen's
    DPI. On certain (virtual) displays it reports screen dimensions of
    0mm x 0mm. In this case users may attempt to fix their screen resolution
    or download the `xdpyinfo` (xorg-xdpyinfo) utility as an alternative to
    `xrandr`. A default DPI of 96 is used otherwise.

Installation options
====================

**Before installing VisPy** you should ensure a working version of python is
installed on your computer, including all of the requirements included in the
**Backend Requirements** section above. A simple way to install most of these
requirements is to install the **Anaconda** scientific python distribution
from Continuum Analytics.
`Anaconda <https://www.anaconda.com/download/>`_ will
install most of the VisPy dependencies for you. If your computer is low on hard
disk space, or you would like a minimal python installation, you may install
the `Miniconda <https://conda.io/miniconda.html>`_ package also from
Continuum Analytics. Once Anaconda is installed, create a
`conda python environment <https://conda.io/docs/user-guide/tasks/manage-python.html>`_.

Via conda
---------

VisPy can be installed in a conda environment by using the package available
from the `conda-forge <https://conda-forge.org/>`_ channel:

.. code-block:: console

    conda install -c conda-forge vispy

Via PyPI
--------

VisPy can also be installed with ``pip`` to install it from PyPI:

.. code-block:: console

    pip install --upgrade vispy

Once the python dependencies have been installed, install the latest
proprietary drivers for your computer's GPU. Generally these drivers may be
downloaded from the GPU manufacturer's website.

.. _dev_install:

Via GitHub
----------

**If you want to run the latest development version**, you can clone the
repository to your local machine and install vispy in "development" mode.
This means that any changes to the cloned repository will be immediately
available in the python environment:

.. code-block:: console

    # creates "vispy" folder
    git clone git://github.com/vispy/vispy.git
    cd vispy
    # install the vispy package in editable/development mode
    pip install -e .

To run the latest development version without cloning the repository, you
can also use this line:

.. code-block:: console

    pip install git+https://github.com/vispy/vispy.git

Via Test PyPI
-------------

The VisPy project uploads the latest development version of the package to
test.pypi.org. This can be a good alternative to the above GitHub installation
process if you don't have or don't want to use git.

You can install these versions of the package by doing:

.. code-block:: console

    pip install --pre -i https://test.pypi.org/simple/ vispy

.. note::

    The main portion of the version number is based on the last public
    release of VisPy so the Test PyPI package may be smaller than when
    the final package is released.

Jupyter Notebook and Lab
------------------------

If you would like to use VisPy in a Jupyter Notebook and have the
visualizations appear inline, we recommend using the "jupyter_rfb" backend.
This backend depends on
`jupyter_rfb library <https://jupyter-rfb.readthedocs.io/en/latest/>`_ which
must be installed before your jupyter notebook or jupyter lab session is
started.

Note that the 'jupyter_rfb' library uses the "remote" jupyter kernel
(the server) to do the drawing of your visualization and then sends the
results to the client (the browser). This means that performance of animations
and user interactions (mouse and keyboard events) will differ depending on the
connection quality between server and client.

.. versionchanged:: 0.8

    The "jupyter_rfb" backend was added in Version 0.8 and the old
    "ipynb_webgl" was removed.

Testing installation
--------------------

It is strongly advised to run the vispy test suite right after installation to
check if everything is ok. To do this, just type:

.. code-block:: python

   >>> import vispy
   >>> vispy.test()
   ...

Please note that the test suite may be unstable on some systems. Any potential
instability in the test suite does not necessarily imply instability in the
working state of the provided VisPy examples.

Usage in an interactive console
===============================

If running from a jupyter console, either the ``jupyter-qtconsole``, the
``jupyter-console``, or, the console within
`Spyder <https://pythonhosted.org/spyder/>`_, you may need to ensure a few
other
`IPython magic <https://ipython.org/ipython-doc/3/interactive/tutorial.html#magic-functions>`_
functions are called prior to using vispy in a given kernel. Before using any
VisPy code, we recommend running the following commands when starting your
python kernel:

.. code-block:: python

     >>> %gui qt
     >>> # your vispy code

Namely, this has the effect of sharing the event loop between application and the interactive
console allowing you use both simultaneously.

Switchable graphics
===================

If your laptop comes with switchable graphics you have to make sure to tell
python to use your graphics card instead of the integrated Intel graphics.
You can identify which graphics card will be used by running:

.. code-block:: python

   >>> import vispy
   >>> print(vispy.sys_info())

and look for Nvidia in the ``GL version``. For example:
``GL version:  '4.6.0 NVIDIA 390.25'``.


Windows
-------

In Windows, you should open the the Nvidia-console and add your specific
python to the list of programs that should use the dedicated graphics card.
Note that this setting is seperate for different conda environments so make
sure you have selected the one you are using VisPy with.

Linux
-----

On Linux with the proprietary Nvidia graphics drivers, you should run python
with ``primusrun python your_script.py``.

For use with a Jupyter kernel, say in Spyder or the ``jupyter-qtconsole``,
make sure the kernel is started with ``primusrun``. For example:

.. code-block:: bash

    $ primusrun spyder3

.. code-block:: bash

    $ primusrun jupyter-qtconsole


Modifying default jupyter kernel
--------------------------------

If you want the jupyter-qtconsole to always use your Nvidia graphics card,
you can change the parameters in the default kernel. To find the default
kernel, run

.. code-block:: bash

   $ jupyter kernelspec list

then edit the ``kernel.json`` file to include ``"primusrun",`` as the first
parameter in ``argv``. For example:

.. code-block:: json

   {
     "argv": [
       "primusrun",
       "python",
       "-m",
       "ipykernel_launcher",
       "-f",
       "{connection_file}"
     ],
     "language": "python",
     "display_name": "Python 3"
   }

Using a similar configuration, you could have two kernels configurations, one
for the dedicated graphics card, and one for the integrated graphics.

Spyder has it's own configuration and I don't know exactly how to make its
console run with ``primusrun`` without running ``primusrun spyder3``.

Embedded System Installation
============================

.. toctree::
  :maxdepth: 1

  raspberry


