# Wiggly Bar
Usage of VisPy to numerically simulate and view a simple physics model.

![GUI Image](http://i.imgur.com/ad0s9lB.png)

This is just a small example, using [VisPy](http://vispy.org) to simulate a system with two springs, a pivot, and a mass. 
The system evolves in a nonlinear fashion, according to two equations:

![Evolution Equations](http://i.imgur.com/8reci4N.png)

In these equations, the J term is the polar moment of inertia of the rod, given by:

![Polar Moment](http://i.imgur.com/94cI1TL.png)

The system has the option to update once every step using the [Euler Method](https://en.wikipedia.org/wiki/Euler_method) or a more stable third-order [Runge-Kutta Method](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods). The instability of the Euler Method becomes apparent as the time step is increased.

### Requirements

 - Python 2.7 or 3.4
 - VisPy 0.5.0 (can be installed following the instructions under "Installation" on the [VisPy github page](https://github.com/vispy/vispy))
 - [NumPy](http://www.numpy.org/)
 - [PyQt4](https://www.riverbankcomputing.com/software/pyqt/intro)
