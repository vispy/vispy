# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Vispy setup script.

Steps to do a new release:

Preparations:
  * Test on Windows, Linux, Mac
  * Make release notes
  * Update API documentation and other docs that need updating.

Test installation:
  * clear the build and dist dir (if they exist)
  * python setup.py register -r http://testpypi.python.org/pypi
  * python setup.py sdist upload -r http://testpypi.python.org/pypi
  * pip install -i http://testpypi.python.org/pypi

Define the version:
  * update __version__ in __init__.py
  * Tag the tip changeset as version x.x

Generate and upload package (preferably on Windows)
  * python setup.py register
  * python setup.py sdist upload
  * python setup.py bdist_wininst upload

Announcing:
  * It can be worth waiting a day for eager users to report critical bugs
  * Announce in scipy-user, vispy mailing list, G+

"""

import os
from os import path as op
try:
    # use setuptools namespace, allows for "develop"
    import setuptools  # noqa, analysis:ignore
except ImportError:
    pass  # it's not essential for installation
from distutils.core import setup

name = 'vispy'
description = 'Interactive visualization in Python'


# Get version and docstring
__version__ = None
__doc__ = ''
docStatus = 0  # Not started, in progress, done
initFile = os.path.join(os.path.dirname(__file__), 'vispy', '__init__.py')
for line in open(initFile).readlines():
    if (line.startswith('__version__')):
        exec(line.strip())
    elif line.startswith('"""'):
        if docStatus == 0:
            docStatus = 1
            line = line.lstrip('"')
        elif docStatus == 1:
            docStatus = 2
    if docStatus == 1:
        __doc__ += line


setup(
    name=name,
    version=__version__,
    author='Vispy contributors',
    author_email='vispy@googlegroups.com',
    license='(new) BSD',
    url='http://vispy.org',
    download_url='https://pypi.python.org/pypi/vispy',
    keywords="visualization OpenGl ES medical imaging 3D plotting "
             "numpy bigdata",
    description=description,
    long_description=__doc__,
    platforms='any',
    provides=['vispy'],
    install_requires=[
        'numpy',
        'PyOpenGl'],
    packages=[
        'vispy',
        'vispy.app', 'vispy.app.tests',
        'vispy.app.backends',
        'vispy.gloo', 'vispy.gloo.tests',
        'vispy.gloo.gl',
        'vispy.scene', 'vispy.scene.tests',
        'vispy.scene.systems',
        'vispy.scene.entities',
        'vispy.scene.cameras',
        'vispy.shaders',
        'vispy.util', 'vispy.util.tests',
        'vispy.util.dataio',
        'vispy.visuals',
        'vispy.openCL',
    ],
    package_dir={
        'vispy': 'vispy'},
    package_data={
        'vispy': [op.join('data', '*'),
                  op.join('app', 'tests', 'qt-designer.ui')]},
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
