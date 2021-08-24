======================================
Installation on Raspberry Pi 3 Model B
======================================


Distribution
============

For this installation a recent `Rasbian Stretch with Desktop
<https://www.raspberrypi.org/downloads/raspbian/>`_ is used. Download the
image and write it onto a fast micro SDHC (class 10) with enough capacity
(at least 16GB).

You might use other distributions for raspberry, but there have been only tests
with Raspbian so far.


Raspbian/Raspberry setup
========================

1. Perform first time startup (language etc.)
2. start `raspi_config` at console and make sure to select the KMS driver
   (Full or Fake). Best experiences were obtained with Full KMS driver::

    7 Advanced Options
        A1 Expand Filesystem - resize root partition to use all SD space
        A7 GL Driver
            G1 (Full KMS) OpenGL desktop driver with full KMS
3. Reboot


Checking OpenGL capabilities
============================

Now start `glxgears` on a console and check the framerate. You should get
something around 60 FPS.

To retrieve more information about the OpenGL status of the system start
`glxinfo` and `glxheads` on a console and observe the output.

Depending in the MESA version (this is something not reliably explored)
there will be the error message::

    libGL error MESA-LOADER failed to retrieve device information

You can ignore this for now, but if you have any information on the source of
this error and how to resolve, please let vispy-devs know.


Backend requirements
====================

VisPy requires at least one toolkit for opening a window and creates an OpenGL
context. This can be done using one Qt, GLFW, SDL2, Wx, or Pyglet.

.. warning::

   For Raspbian/Raspberry we rely on Qt4 for now!


Package requirements
====================

The only mandatory requirement for VisPy is the `numpy <http://numpy.org>`_
package. This is already distributed with Raspbian. Nevertheless you need to
install some system packages to get VisPy compiled, installed and running:

- `python3-pyqt4` - Python3 bindings for Qt4
- `python3-pyqt4-opengl` - Python3 bindings for Qt's OpenGL module
- `cython3` - C-Extensions for Python3

Please use the Raspbian package manager to retrieve these packages.


Installation options
====================

You have several options to install VisPy. Make sure to use the system ``python3``
at all times. We recommend to use the latest development version.

**To install the latest release version**, you can do:

.. code-block:: console

   $ pip3 install --upgrade vispy

**If you want to run the latest development version**, you can clone the
repository to your local machine and install with ``develop`` to enable easy
updates to latest ``main``:

.. code-block:: console

   $ git clone git://github.com/vispy/vispy.git  # creates "vispy" folder
   $ cd vispy
   $ python3 setup.py develop

To run the latest development version without cloning the repository, you
can also use this line:

.. code-block:: console

   $ pip3 install git+https://github.com/vispy/vispy.git


Testing installation
====================

It is strongly advised to run the vispy test suite right after installation to
check if everything is ok. To do this, just type:

.. code-block:: python

   >>> import vispy
   >>> vispy.test()
   ...

Please note that the test suite may be unstable on some systems. Any potential
instability in the test suite does not necessarily imply instability in the
working state of the provided VisPy examples.

If you have feedback or questions, please use the VisPy :doc:`community` channels.
