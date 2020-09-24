# Release Notes

## [v0.6.5](https://github.com/vispy/vispy/tree/v0.6.5) (2020-09-23)

- Patch release to create Python 3.8 wheels and future proof pyproject.toml

## [v0.6.4](https://github.com/vispy/vispy/tree/v0.6.4) (2019-12-13)

**Enhancements:**

- Filter unnecessary QSocketNotifier warning when using QtConsole [\#1789](https://github.com/vispy/vispy/pull/1789) ([hmaarrfk](https://github.com/hmaarrfk))
- FIX: Nest triangle and skimage imports [\#1781](https://github.com/vispy/vispy/pull/1781) ([larsoner](https://github.com/larsoner))
- Switch to setuptools\_scm version.py usage to avoid import overhead [\#1780](https://github.com/vispy/vispy/pull/1780) ([djhoese](https://github.com/djhoese))

**Fixed bugs:**

- Skip bad font in test\_font [\#1772](https://github.com/vispy/vispy/pull/1772) ([hmaarrfk](https://github.com/hmaarrfk))


## [v0.6.3](https://github.com/vispy/vispy/tree/v0.6.3) (2019-11-27)

**Enhancements:**

- Improve AxisVisual visual by providing property getters and setters [\#1744](https://github.com/vispy/vispy/pull/1744) ([astrofrog](https://github.com/astrofrog))
- Fix MarkerVisual scaling when rotating in 3D space [\#1702](https://github.com/vispy/vispy/pull/1702) ([sofroniewn](https://github.com/sofroniewn))

**Fixed bugs:**

- Fix string formatting of array shape [\#1768](https://github.com/vispy/vispy/pull/1768) ([cgohlke](https://github.com/cgohlke))
- Fix texture alignment to use data itemsize [\#1758](https://github.com/vispy/vispy/pull/1758) ([djhoese](https://github.com/djhoese))
- Fix shader version handling in webgl backend [\#1756](https://github.com/vispy/vispy/pull/1756) ([djhoese](https://github.com/djhoese))
- Fix 2D mesh bounds IndexError when viewed in 3D [\#1749](https://github.com/vispy/vispy/pull/1749) ([sofroniewn](https://github.com/sofroniewn))
- Fix xaxis labels being wrong initially in PlotWidget [\#1748](https://github.com/vispy/vispy/pull/1748) ([tlambert03](https://github.com/tlambert03))
- Various bug fixes related to AxisVisual [\#1743](https://github.com/vispy/vispy/pull/1743) ([astrofrog](https://github.com/astrofrog))
- Fixed a bug in linking two flycameras [\#1557](https://github.com/vispy/vispy/pull/1557) ([SuyiWang](https://github.com/SuyiWang))

**Merged pull requests:**

- Fix additional numpy warnings when dealing with dtypes of size 1 [\#1766](https://github.com/vispy/vispy/pull/1766) ([djhoese](https://github.com/djhoese))


## [v0.6.2](https://github.com/vispy/vispy/tree/v0.6.2) (2019-11-04)

**Enhancements:**

- Switch to setuptools\_scm for automatic version numbering [\#1706](https://github.com/vispy/vispy/pull/1706) ([djhoese](https://github.com/djhoese))
- Improve PanZoom camera performance when non-+z direction is used [\#1682](https://github.com/vispy/vispy/pull/1682) ([os-gabe](https://github.com/os-gabe))

**Fixed bugs:**

- Fix Python 3.8 compatibility in Canvas 'keys' update [\#1730](https://github.com/vispy/vispy/pull/1730) ([GuillaumeFavelier](https://github.com/GuillaumeFavelier))
- Fix VolumeVisual modifying user provided data in-place [\#1728](https://github.com/vispy/vispy/pull/1728) ([tlambert03](https://github.com/tlambert03))
- Fix depth buffer precision [\#1724](https://github.com/vispy/vispy/pull/1724) ([h3fang](https://github.com/h3fang))
- Volume visual has unset variable texture2D\_LUT [\#1712](https://github.com/vispy/vispy/pull/1712) ([liuyenting](https://github.com/liuyenting))
- Fix MarkersVisual.set\_data crash when pos is None [\#1703](https://github.com/vispy/vispy/pull/1703) ([proto3](https://github.com/proto3))
- Fix numpy futurewarning in dtype creation [\#1691](https://github.com/vispy/vispy/pull/1691) ([djhoese](https://github.com/djhoese))


## v0.6.1

- Fix discrete colormap ordering (#1668)
- Fix various examples (#1671, #1676)
- Fix Jupyter extension zoom direction (#1679)


## v0.6.0

- Update PyQt5/PySide2 to use newer GL API
- Update to PyQt5 as default backend
- New Cython-based text rendering option
- New WindbarbVisual
- Improved JupyterLab/Notebook widget (experimental)
- Fix various memory leaks
- Various optimizations and bug fixes


## v0.5.3

- Workaround added to fix ImportError with matplotlib 2.2+ (#1437)


## v0.5.2

- Fix PyPI packaging to include LICENSE.txt
- Fix initial axis limits in PlotWidget (#1386)
- Fix zoom event position in Pyglet backend (#1388)
- Fix camera importing (#1389, #1172)
- Refactor `EllipseVisual` and `RectangleVisual` (#1387, #1349)
- Fix `one_scene_four_cams.py` example (#1391, #1124)
- Add `two_qt_widgets.py` example (#1392, #1298)
- Fix order of alignment values for proper processing (#1395, #641)


## v0.5.1

- Fix 'doc' directory being installed with source tarball
- Fix 'ArrowVisual' when used with a Scene camera and in 3D space
- Fix 'SphereVisual' rows/cols order in 'latitude' method
- Fix DPI calculation on linux when xrandr returns 0mm screen dimension


## v0.5.0

- Major refactor of all cameras and visuals
- Add support for wxPython 4.0+ (project phoenix)
- Improve Jupyter Notebook support (not full support)
- Improve Python 3 support
- Add colormaps
- Add various new visuals `GridMesh`, `BoxVisual`, `PlaneVisual`, etc.
- Various bug fixes and performance improvements (177+ pull requests)
- Remove experimental matplotlib backend (`mpl_plot`)
- Drop Python 2.6 support


## v0.4.0

There have been many changes, which include:

- minor tweaks and bugfixes to gloo
- experimental support for "collections" (batched GL draw calls)
- many new Visuals (Volume, Isocurve, etc.)
- improvements and extensions of the SceneGraph system
- proper HiDPI support
- an experimental native high-level plotting interface vispy.plot


## v0.3.0

Many changes:

- Added multiple new application backends, including a IPython browser
  backend.
- Experimental support for high-level visualizations through
  '`vispy.scene`` and ``vispy.scene.visuals``.
- Experimental support for matplotlib plotting through ``vispy.mpl_plot``.
- Loads of bugfixes.


## v0.2.1

Small fix in the setup script. The buf prevented pip from working.


## v0.2.0

In this release we focussed on improving and finalizing the object
oriented OpenGL interface ``vispy.gloo``. Some major (backward
incompatible) changes were done. However, from this release we consider
the ``vispy.gloo`` package relatively stable and we try to minimize
backward incompatibilities.

Changes in more detail:

- ``vispy.oogl`` is renamed to ``vispy.gloo``
- ``vispy.gl`` is moved to ``vispy.gloo.gl`` since most users will
  use gloo to interface with OpenGL.
- Improved (and thus changed) several parts of the gloo API.
- Some parts of gloo were refactored and should be more robust.
- Much better coverage of the test suite.
- Compatibility with Python 2.6 (Jerome Kieffer)
- More examples and a gallery on the website to show them off. 


## v0.1.0

First release. We have an initial version of the object oriented interface
to OpenGL, called `vispy.oogl`.


\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
