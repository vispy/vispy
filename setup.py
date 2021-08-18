# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Vispy setup script.

Steps to do a new release:

Preparations:
  * Test on Windows, Linux, Mac
  * Make release notes
  * Update API documentation and other docs that need updating.

Define the version and release:
  * tag the tip changeset as version x.x.x; `git tag -a 'vX.Y.Z' -m "Version X.Y.Z"`
  * push tag to github
  * verify that azure pipelines complete
  * verify that `.tar.gz` sdist and binary wheels are available on PyPI

Announcing:
  * It can be worth waiting a day for eager users to report critical bugs
  * Announce in scipy-user, vispy mailing list, twitter (@vispyproject)

"""

import os
import sys
import platform
from os import path as op
from distutils import log
from setuptools import setup, find_packages, Command, Extension
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from subprocess import check_call

import numpy as np
from Cython.Build import cythonize

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

name = 'vispy'
description = 'Interactive visualization in Python'

# Special commands for building jupyter notebook extension
here = os.path.dirname(os.path.abspath(__file__))
node_root = os.path.join(here, 'js')
is_repo = os.path.exists(os.path.join(here, '.git'))

npm_path = os.pathsep.join([
    os.path.join(node_root, 'node_modules', '.bin'),
    os.environ.get('PATH', os.defpath),
])


def set_builtin(name, value):
    if isinstance(__builtins__, dict):
        __builtins__[name] = value
    else:
        setattr(__builtins__, name, value)


def js_prerelease(command, strict=False):
    """Decorator for building minified js/css prior to another command."""
    class DecoratedCommand(command):
        def run(self):
            jsdeps = self.distribution.get_command_obj('jsdeps')
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return

            try:
                self.distribution.run_command('jsdeps')
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    log.warn('rebuilding js and css failed')
                    if missing:
                        log.error('missing files: %s' % missing)
                    # HACK: Allow users who can't build the JS to still install vispy
                    if not is_repo:
                        raise e
                    log.warn('WARNING: continuing installation WITHOUT nbextension javascript')
                    # remove JS files from data_files so setuptools doesn't try to copy
                    # non-existent files
                    self.distribution.data_files = [x for x in self.distribution.data_files
                                                    if 'jupyter' not in x[0]]
                else:
                    log.warn('rebuilding js and css failed (not a problem)')
                    log.warn(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return DecoratedCommand


def update_package_data(distribution):
    """Update package_data to catch changes during setup."""
    build_py = distribution.get_command_obj('build_py')
    # distribution.package_data = find_package_data()
    # re-init build_py options which load package_data
    build_py.finalize_options()


class NPM(Command):
    description = 'install package.json dependencies using npm'

    user_options = []

    node_modules = os.path.join(node_root, 'node_modules')

    targets = [
        os.path.join(here, 'vispy', 'static', 'extension.js'),
        os.path.join(here, 'vispy', 'static', 'index.js')
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_npm_name(self):
        npmName = 'npm'
        if platform.system() == 'Windows':
            npmName = 'npm.cmd'

        return npmName

    def has_npm(self):
        npmName = self.get_npm_name()
        try:
            check_call([npmName, '--version'])
            return True
        except BaseException:
            return False

    def should_run_npm_install(self):
        # package_json = os.path.join(node_root, 'package.json')
        # node_modules_exists = os.path.exists(self.node_modules)
        return self.has_npm()

    def run(self):
        has_npm = self.has_npm()
        if not has_npm:
            log.error("`npm` unavailable.  If you're running this command "
                      "using sudo, make sure `npm` is available to sudo")

        env = os.environ.copy()
        env['PATH'] = npm_path

        if self.should_run_npm_install():
            log.info("Installing build dependencies with npm.  This may take "
                     "a while...")
            npmName = self.get_npm_name()
            check_call([npmName, 'install', '--verbose'], cwd=node_root,
                       stdout=sys.stdout, stderr=sys.stderr)
            os.utime(self.node_modules, None)

        for t in self.targets:
            if not os.path.exists(t):
                msg = 'Missing file: %s' % t
                if not has_npm:
                    msg += '\nnpm is required to build a development ' \
                           'version of a widget extension'
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)


extensions = [Extension('vispy.visuals.text._sdf_cpu',
                        [op.join('vispy', 'visuals', 'text', '_sdf_cpu.pyx')],
                        include_dirs=[np.get_include()]),
              ]

readme = open('README.rst', 'r').read()
setup(
    name=name,
    use_scm_version={
        'write_to': 'vispy/version.py',
        # uses setuptools_scm.version.get_local_dirty_tag (+dirty or empty string)
        'local_scheme': 'dirty-tag',
    },
    author='Vispy contributors',
    author_email='vispy@googlegroups.com',
    license='(new) BSD',
    url='http://vispy.org',
    download_url='https://pypi.python.org/pypi/vispy',
    keywords=[
        'visualization',
        'OpenGl',
        'ES',
        'medical',
        'imaging',
        '3D',
        'plotting',
        'numpy',
        'bigdata',
        'ipython',
        'jupyter',
        'widgets',
    ],
    description=description,
    long_description=readme,
    platforms='any',
    provides=['vispy'],
    cmdclass={
        'build_py': js_prerelease(build_py),
        'egg_info': js_prerelease(egg_info),
        'sdist': js_prerelease(sdist, strict=True),
        'jsdeps': NPM,
    },
    python_requires='>=3.6',
    install_requires=['numpy', 'freetype-py', 'hsluv', 'kiwisolver'],
    setup_requires=['numpy', 'cython', 'setuptools_scm', 'setuptools_scm_git_archive'],
    extras_require={
        'ipython-static': ['ipython'],
        'ipython-vnc': ['ipython>=7'],
        'ipython-webgl': ['ipywidgets>=7.0', 'ipython>=7', 'tornado'],
        'pyglet': ['pyglet>=1.2'],
        'pyqt5': ['pyqt5'],
        'pyside': ['PySide'],
        'pyside2': ['PySide2'],
        'pyside6': ['PySide6'],
        'sdl2': ['PySDL2'],
        'wx': ['wxPython'],
        'tk': ['pyopengltk'],
        'doc': ['pydata-sphinx-theme', 'numpydoc', 'sphinxcontrib-apidoc'],
        'io': ['meshio', 'Pillow'],
    },
    packages=find_packages(exclude=['make']),
    ext_modules=cythonize(extensions),
    package_dir={'vispy': 'vispy'},
    data_files=[
        ('share/jupyter/nbextensions/vispy', [
            'vispy/static/extension.js',
            'vispy/static/index.js',
            'vispy/static/index.js.map',
        ]),
        ('etc/jupyter/nbconfig/notebook.d', ['vispy.json']),
    ],
    include_package_data=True,
    package_data={
        'vispy': [op.join('io', '_data', '*'),
                  op.join('html', 'static', 'js', '*'),
                  op.join('app', 'tests', 'qt-designer.ui'),
                  op.join('util', 'fonts', 'data', '*.ttf'),
                  ],

        'vispy.glsl': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.antialias': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.arrowheads': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.arrows': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.collections': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.colormaps': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.lines': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.markers': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.math': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.misc': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.transforms': ['*.vert', '*.frag', "*.glsl"],

    },
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: IPython'
    ],
)
