# Release Notes

## [v0.15.1](https://github.com/vispy/vispy/tree/v0.15.1) (2025-05-15)

**Fixed bugs:**

- Restore sdist upload to pypi  [\#2672](https://github.com/vispy/vispy/pull/2672) ([Czaki](https://github.com/Czaki))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.23.2 to 2.23.3 [\#2669](https://github.com/vispy/vispy/pull/2669) ([dependabot[bot]](https://github.com/apps/dependabot))


## [v0.15.0](https://github.com/vispy/vispy/tree/v0.15.0) (2025-04-22)

**Enhancements:**

- Add high and low color settings for colormaps \(HiLo mapping\) [\#2663](https://github.com/vispy/vispy/pull/2663) ([brisvag](https://github.com/brisvag))
- Allow setting bad color on colormap \(continue \#2620\) [\#2659](https://github.com/vispy/vispy/pull/2659) ([brisvag](https://github.com/brisvag))
- Add modifiers to QT native gesture events [\#2631](https://github.com/vispy/vispy/pull/2631) ([arambert](https://github.com/arambert))
- Implement limiting size for gridlines \(2\) [\#2630](https://github.com/vispy/vispy/pull/2630) ([brisvag](https://github.com/brisvag))
- Various optimizations related to camera linking and mesh normals [\#2532](https://github.com/vispy/vispy/pull/2532) ([djhoese](https://github.com/djhoese))

**Fixed bugs:**

- Fix bad\_color handling and simplify some logic [\#2662](https://github.com/vispy/vispy/pull/2662) ([brisvag](https://github.com/brisvag))
- Fix type of vertice passed to function for adding triangles [\#2647](https://github.com/vispy/vispy/pull/2647) ([Czaki](https://github.com/Czaki))
- Fix mesh colors reshaping [\#2645](https://github.com/vispy/vispy/pull/2645) ([BenZickel](https://github.com/BenZickel))
- Use visual coordinates in ArcballCamera [\#2642](https://github.com/vispy/vispy/pull/2642) ([Seon82](https://github.com/Seon82))
- fix: prevent zerodiv error when auto-calculating clims in scalable textures [\#2621](https://github.com/vispy/vispy/pull/2621) ([tlambert03](https://github.com/tlambert03))
- Set self.\_data\_dtype in scale\_and\_set\_data for CPU scaled textures [\#2601](https://github.com/vispy/vispy/pull/2601) ([aganders3](https://github.com/aganders3))
- Ignore unhandled Qt events [\#2600](https://github.com/vispy/vispy/pull/2600) ([gselzer](https://github.com/gselzer))
- Ignore all flat triangles in triangulation [\#2248](https://github.com/vispy/vispy/pull/2248) ([andy-sweet](https://github.com/andy-sweet))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.23.1 to 2.23.2 [\#2660](https://github.com/vispy/vispy/pull/2660) ([dependabot[bot]](https://github.com/apps/dependabot))
- Fix small mistake in docs [\#2658](https://github.com/vispy/vispy/pull/2658) ([jspast](https://github.com/jspast))
- Bump pypa/cibuildwheel from 2.23.0 to 2.23.1 [\#2655](https://github.com/vispy/vispy/pull/2655) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.22.0 to 2.23.0 [\#2652](https://github.com/vispy/vispy/pull/2652) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.21.2 to 2.22.0 [\#2632](https://github.com/vispy/vispy/pull/2632) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump mamba-org/setup-micromamba from 1 to 2 [\#2626](https://github.com/vispy/vispy/pull/2626) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.21.1 to 2.21.2 [\#2625](https://github.com/vispy/vispy/pull/2625) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.21.0 to 2.21.1 [\#2623](https://github.com/vispy/vispy/pull/2623) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.20.0 to 2.21.0 [\#2622](https://github.com/vispy/vispy/pull/2622) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.19.2 to 2.20.0 [\#2611](https://github.com/vispy/vispy/pull/2611) ([dependabot[bot]](https://github.com/apps/dependabot))
- Add variable name in errors to help debugging [\#2605](https://github.com/vispy/vispy/pull/2605) ([brisvag](https://github.com/brisvag))
- Bump pypa/cibuildwheel from 2.19.1 to 2.19.2 [\#2604](https://github.com/vispy/vispy/pull/2604) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.18.1 to 2.19.1 [\#2602](https://github.com/vispy/vispy/pull/2602) ([dependabot[bot]](https://github.com/apps/dependabot))


## [v0.14.3](https://github.com/vispy/vispy/tree/v0.14.3) (2024-06-17)

**Enhancements:**

- Clip step size based on maximum detail on an 8K monitor [\#2589](https://github.com/vispy/vispy/pull/2589) ([jni](https://github.com/jni))

**Fixed bugs:**

- Fix integral computation in attenuated mip [\#2588](https://github.com/vispy/vispy/pull/2588) ([jni](https://github.com/jni))
- Reset VertexAttribDivisor even if None [\#2583](https://github.com/vispy/vispy/pull/2583) ([aganders3](https://github.com/aganders3))

**Merged pull requests:**

- Fix CI: failing tests and linting errors not failing checks [\#2597](https://github.com/vispy/vispy/pull/2597) ([aganders3](https://github.com/aganders3))
- Bump pypa/cibuildwheel from 2.18.0 to 2.18.1 [\#2586](https://github.com/vispy/vispy/pull/2586) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.17.0 to 2.18.0 [\#2584](https://github.com/vispy/vispy/pull/2584) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump peaceiris/actions-gh-pages from 3 to 4 [\#2582](https://github.com/vispy/vispy/pull/2582) ([dependabot[bot]](https://github.com/apps/dependabot))
- Fix gallery link in README.rst [\#2579](https://github.com/vispy/vispy/pull/2579) ([inigoalonso](https://github.com/inigoalonso))
- Bump pypa/cibuildwheel from 2.16.5 to 2.17.0 [\#2578](https://github.com/vispy/vispy/pull/2578) ([dependabot[bot]](https://github.com/apps/dependabot))


## [v0.14.2](https://github.com/vispy/vispy/tree/v0.14.2) (2024-03-14)

**Enhancements:**

- Radius of ellipse can now be specified as numpy.array [\#2561](https://github.com/vispy/vispy/pull/2561) ([ullmannJan](https://github.com/ullmannJan))
- Add ivec2, ivec3, ivec4 to ATYPEINFO in glir.py [\#2545](https://github.com/vispy/vispy/pull/2545) ([hmaarrfk](https://github.com/hmaarrfk))
- Improve Markers symbols validation performance [\#2533](https://github.com/vispy/vispy/pull/2533) ([Czaki](https://github.com/Czaki))

**Fixed bugs:**

- Correction to Vispy.Visuals.Markers.set\_data [\#2565](https://github.com/vispy/vispy/pull/2565) ([c40zAtGitHub](https://github.com/c40zAtGitHub))
- Fix SurfacePlotVisual not allowing 2D x and y inputs [\#2554](https://github.com/vispy/vispy/pull/2554) ([ullmannJan](https://github.com/ullmannJan))
- Change `devicePixelRatio` calls to `devicePixelRatioF` to get a floating point number instead of an integer [\#2540](https://github.com/vispy/vispy/pull/2540) ([dalthviz](https://github.com/dalthviz))

**Merged pull requests:**

- Fix a few typos in the docs [\#2573](https://github.com/vispy/vispy/pull/2573) ([kraasch](https://github.com/kraasch))
- Bump pypa/cibuildwheel from 2.16.4 to 2.16.5 [\#2572](https://github.com/vispy/vispy/pull/2572) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.16.2 to 2.16.4 [\#2571](https://github.com/vispy/vispy/pull/2571) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/cache from 3 to 4 [\#2569](https://github.com/vispy/vispy/pull/2569) ([dependabot[bot]](https://github.com/apps/dependabot))
- Fix typo in plot widget error message [\#2563](https://github.com/vispy/vispy/pull/2563) ([jeertmans](https://github.com/jeertmans))
- Bump actions/upload-artifact from 3 to 4 [\#2559](https://github.com/vispy/vispy/pull/2559) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/setup-python from 4 to 5 [\#2556](https://github.com/vispy/vispy/pull/2556) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.16.1 to 2.16.2 [\#2536](https://github.com/vispy/vispy/pull/2536) ([dependabot[bot]](https://github.com/apps/dependabot))


## [v0.14.1](https://github.com/vispy/vispy/tree/v0.14.1) (2023-10-03)

**Fixed bugs:**

- return to oldest supported numpy [\#2535](https://github.com/vispy/vispy/pull/2535) ([brisvag](https://github.com/brisvag))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.16.0 to 2.16.1 [\#2534](https://github.com/vispy/vispy/pull/2534) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.15.0 to 2.16.0 [\#2531](https://github.com/vispy/vispy/pull/2531) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump docker/setup-qemu-action from 2 to 3 [\#2529](https://github.com/vispy/vispy/pull/2529) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/checkout from 3 to 4 [\#2527](https://github.com/vispy/vispy/pull/2527) ([dependabot[bot]](https://github.com/apps/dependabot))


## [v0.14.0](https://github.com/vispy/vispy/tree/v0.14.0) (2023-09-08)

**Enhancements:**

- Remove deprecated code from vispy.color.get\_colormap [\#2519](https://github.com/vispy/vispy/pull/2519) ([codypiersall](https://github.com/codypiersall))
- Cache make\_pattern on DashAtlas [\#2508](https://github.com/vispy/vispy/pull/2508) ([aganders3](https://github.com/aganders3))
- Add push/pop gl\_state for visuals \(used in picking\) [\#2502](https://github.com/vispy/vispy/pull/2502) ([aganders3](https://github.com/aganders3))
- Add primitive picking filters for Mesh and Markers visuals [\#2500](https://github.com/vispy/vispy/pull/2500) ([aganders3](https://github.com/aganders3))

**Fixed bugs:**

- Fix spherical markers depth buffer with scaling='visual' [\#2506](https://github.com/vispy/vispy/pull/2506) ([brisvag](https://github.com/brisvag))
- Update \_glfw.py [\#2496](https://github.com/vispy/vispy/pull/2496) ([smyeungx](https://github.com/smyeungx))
- Fix mesh shading with flipped normals [\#2493](https://github.com/vispy/vispy/pull/2493) ([brisvag](https://github.com/brisvag))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.14.1 to 2.15.0 and add Python 3.12 wheels [\#2515](https://github.com/vispy/vispy/pull/2515) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.14.0 to 2.14.1 [\#2509](https://github.com/vispy/vispy/pull/2509) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.13.1 to 2.14.0 [\#2507](https://github.com/vispy/vispy/pull/2507) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.13.0 to 2.13.1 [\#2498](https://github.com/vispy/vispy/pull/2498) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.12.3 to 2.13.0 [\#2492](https://github.com/vispy/vispy/pull/2492) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump mamba-org/provision-with-micromamba from 15 to 16 [\#2490](https://github.com/vispy/vispy/pull/2490) ([dependabot[bot]](https://github.com/apps/dependabot))
- Add lasso selection example [\#2485](https://github.com/vispy/vispy/pull/2485) ([DanAurea](https://github.com/DanAurea))

## [v0.13.0](https://github.com/vispy/vispy/tree/v0.13.0) (2023-05-12)

**Enhancements:**

- Switch MarkersVisual scaling option to string "fixed", "scene", or "visual" [\#2470](https://github.com/vispy/vispy/pull/2470) ([djhoese](https://github.com/djhoese))
- Add early-termination optimization to attenuated mip [\#2465](https://github.com/vispy/vispy/pull/2465) ([aganders3](https://github.com/aganders3))
- Add `InstancedMeshVisual` for faster and easier rendering of repeated meshes [\#2461](https://github.com/vispy/vispy/pull/2461) ([brisvag](https://github.com/brisvag))
- Instanced mesh example [\#2460](https://github.com/vispy/vispy/pull/2460) ([brisvag](https://github.com/brisvag))
- Use QNativeEventGesture for touchpad gesture input [\#2456](https://github.com/vispy/vispy/pull/2456) ([aganders3](https://github.com/aganders3))

**Fixed bugs:**

- Fix TypeError with pinch-to-zoom [\#2483](https://github.com/vispy/vispy/pull/2483) ([aganders3](https://github.com/aganders3))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.12.1 to 2.12.3 [\#2472](https://github.com/vispy/vispy/pull/2472) ([dependabot[bot]](https://github.com/apps/dependabot))
- Cleanup site navbar with pydata-sphinx-theme 0.10+ [\#2371](https://github.com/vispy/vispy/pull/2371) ([djhoese](https://github.com/djhoese))

## [v0.12.2](https://github.com/vispy/vispy/tree/v0.12.2) (2023-03-20)

**Enhancements:**

- Clean up and test computation of normals in MeshData [\#2444](https://github.com/vispy/vispy/pull/2444) ([asnt](https://github.com/asnt))
- Vectorize MeshData vertex normals computation [\#2434](https://github.com/vispy/vispy/pull/2434) ([asnt](https://github.com/asnt))

**Fixed bugs:**

- Fix shader compilation error for MeshVisual when mesh.clim = 'auto' [\#2463](https://github.com/vispy/vispy/pull/2463) ([aganders3](https://github.com/aganders3))
- Bugfix: Use color.lower\(\) for \_color\_dict keys [\#2459](https://github.com/vispy/vispy/pull/2459) ([psobolewskiPhD](https://github.com/psobolewskiPhD))
- Fix f-string missing prefix in gloo/program.py error message [\#2457](https://github.com/vispy/vispy/pull/2457) ([aganders3](https://github.com/aganders3))
- Fix character codec error on Windows Python \<3.10 [\#2437](https://github.com/vispy/vispy/pull/2437) ([haesleinhuepf](https://github.com/haesleinhuepf))

**Merged pull requests:**

- Bump pypa/cibuildwheel from 2.12.0 to 2.12.1 [\#2462](https://github.com/vispy/vispy/pull/2462) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.11.4 to 2.12.0 [\#2447](https://github.com/vispy/vispy/pull/2447) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump mamba-org/provision-with-micromamba from 14 to 15 [\#2446](https://github.com/vispy/vispy/pull/2446) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.11.3 to 2.11.4 [\#2441](https://github.com/vispy/vispy/pull/2441) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.11.2 to 2.11.3 [\#2438](https://github.com/vispy/vispy/pull/2438) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump docker/setup-qemu-action from 1 to 2 [\#2432](https://github.com/vispy/vispy/pull/2432) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump pypa/cibuildwheel from 2.1.1 to 2.11.2 [\#2431](https://github.com/vispy/vispy/pull/2431) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v0.12.1](https://github.com/vispy/vispy/tree/v0.12.1) (2022-11-14)

**Fixed bugs:**

- Fix: bug with new Markers.symbol and empty data [\#2428](https://github.com/vispy/vispy/pull/2428) ([brisvag](https://github.com/brisvag))

## [v0.12.0](https://github.com/vispy/vispy/tree/v0.12.0) (2022-11-08)

**Enhancements:**

- Scale values when calculating attenuation in attenuated\_mip shader [\#2417](https://github.com/vispy/vispy/pull/2417) ([aganders3](https://github.com/aganders3))
- clipping planes performance: do not create a new function willy nilly [\#2383](https://github.com/vispy/vispy/pull/2383) ([brisvag](https://github.com/brisvag))
- Instance rendering in gloo. [\#2378](https://github.com/vispy/vispy/pull/2378) ([brisvag](https://github.com/brisvag))
- Allow setting array to `symbol` in `MarkersVisual` [\#2361](https://github.com/vispy/vispy/pull/2361) ([brisvag](https://github.com/brisvag))

**Fixed bugs:**

- Improve PySide6 Support: swapBehavior for DoubleBuffer, BUTTONMAP as pyqt6, xfail test\_context [\#2411](https://github.com/vispy/vispy/pull/2411) ([psobolewskiPhD](https://github.com/psobolewskiPhD))
- fix: wx timer from float to int [\#2396](https://github.com/vispy/vispy/pull/2396) ([Bliss3d](https://github.com/Bliss3d))
- Fix custom image interpolation kernels to work with negative numbers [\#2382](https://github.com/vispy/vispy/pull/2382) ([brisvag](https://github.com/brisvag))
- Use correct regex when parsing variables [\#2380](https://github.com/vispy/vispy/pull/2380) ([brisvag](https://github.com/brisvag))
- Update tube.py to support Python 3.10 and higher. [\#2370](https://github.com/vispy/vispy/pull/2370) ([tralfaz](https://github.com/tralfaz))
- Fix marker size with anisotropic scaling [\#2359](https://github.com/vispy/vispy/pull/2359) ([brisvag](https://github.com/brisvag))
- Fix MouseEvent `.buttons` not including triggering mouse button [\#2355](https://github.com/vispy/vispy/pull/2355) ([tushar5526](https://github.com/tushar5526))
- Implement turntable camera `roll` programmatically and clarify transformation docstrings [\#2352](https://github.com/vispy/vispy/pull/2352) ([harripj](https://github.com/harripj))
- Fix dtype casting for Texture objects [\#2350](https://github.com/vispy/vispy/pull/2350) ([brisvag](https://github.com/brisvag))

**Merged pull requests:**

- Bump mamba-org/provision-with-micromamba from 7 to 14 [\#2425](https://github.com/vispy/vispy/pull/2425) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/setup-python from 2 to 4 [\#2424](https://github.com/vispy/vispy/pull/2424) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/checkout from 2 to 3 [\#2423](https://github.com/vispy/vispy/pull/2423) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/download-artifact from 2 to 3 [\#2422](https://github.com/vispy/vispy/pull/2422) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump actions/upload-artifact from 2 to 3 [\#2421](https://github.com/vispy/vispy/pull/2421) ([dependabot[bot]](https://github.com/apps/dependabot))
- Allow 180 fov and clarify docstring [\#2412](https://github.com/vispy/vispy/pull/2412) ([brisvag](https://github.com/brisvag))
- Address deprecation warnings with the usage of distuilts for LooseVersion [\#2404](https://github.com/vispy/vispy/pull/2404) ([hmaarrfk](https://github.com/hmaarrfk))
- Add governance and steering committee information to README [\#2397](https://github.com/vispy/vispy/pull/2397) ([djhoese](https://github.com/djhoese))
- New instanced rendering example [\#2376](https://github.com/vispy/vispy/pull/2376) ([brisvag](https://github.com/brisvag))
- Add initial organization charter and project governance [\#2367](https://github.com/vispy/vispy/pull/2367) ([djhoese](https://github.com/djhoese))
- Fix a few comment and docstring typos [\#2353](https://github.com/vispy/vispy/pull/2353) ([timgates42](https://github.com/timgates42))
- Use `cubic` instead of `bicubic` as name for interpolation [\#2348](https://github.com/vispy/vispy/pull/2348) ([brisvag](https://github.com/brisvag))
- Fix test for `Image` custom interpolation [\#2347](https://github.com/vispy/vispy/pull/2347) ([brisvag](https://github.com/brisvag))
- Add realtime data visualization tutorial examples [\#2339](https://github.com/vispy/vispy/pull/2339) ([djhoese](https://github.com/djhoese))

## [v0.11.0](https://github.com/vispy/vispy/tree/v0.11.0) (2022-07-04)

**Enhancements:**

- Reduce memory copies in LineVisual [\#2327](https://github.com/vispy/vispy/pull/2327) ([christiansandberg](https://github.com/christiansandberg))
- Add shader interpolation methods for VolumeVisual [\#2322](https://github.com/vispy/vispy/pull/2322) ([brisvag](https://github.com/brisvag))
- Add 'custom' ImageVisual interpolation with custom kernel on GPU [\#2319](https://github.com/vispy/vispy/pull/2319) ([brisvag](https://github.com/brisvag))

**Fixed bugs:**

- Fix clipping planes logic for `Volume` and `PlanesClipper` [\#2329](https://github.com/vispy/vispy/pull/2329) ([brisvag](https://github.com/brisvag))
- Enable text depth testing [\#2328](https://github.com/vispy/vispy/pull/2328) ([almarklein](https://github.com/almarklein))
- Fix HIDPI on pyglet [\#2326](https://github.com/vispy/vispy/pull/2326) ([almarklein](https://github.com/almarklein))
- Add `blend_equation` \(add\) to GL\_PRESETS [\#2324](https://github.com/vispy/vispy/pull/2324) ([psobolewskiPhD](https://github.com/psobolewskiPhD))

**Merged pull requests:**

- Fix link to CHANGELOG.md in README.rst [\#2338](https://github.com/vispy/vispy/pull/2338) ([psobolewskiPhD](https://github.com/psobolewskiPhD))
- Typo fix in docstring [\#2332](https://github.com/vispy/vispy/pull/2332) ([ksohan](https://github.com/ksohan))

## [v0.10.0](https://github.com/vispy/vispy/tree/v0.10.0) (2022-04-18)

**Enhancements:**

- Add GL\_MIN/GL\_MAX constants for glBlendEquation [\#2320](https://github.com/vispy/vispy/pull/2320) ([djhoese](https://github.com/djhoese))
- Add cutoff to mip and minip volume projection for fragment discard [\#2308](https://github.com/vispy/vispy/pull/2308) ([brisvag](https://github.com/brisvag))
- Optimize shader regular expression compilation [\#2297](https://github.com/vispy/vispy/pull/2297) ([PydPiper](https://github.com/PydPiper))
- Add ComplexImageVisual for viewing complex image data [\#1999](https://github.com/vispy/vispy/pull/1999) ([tlambert03](https://github.com/tlambert03))
- Allow depth in Texture2D. [\#1310](https://github.com/vispy/vispy/pull/1310) ([keunhong](https://github.com/keunhong))

**Fixed bugs:**

- Set depth in `VolumeVisual` for `mip`/`minip`/`attenuated_mip` rendering modes [\#2305](https://github.com/vispy/vispy/pull/2305) ([alisterburt](https://github.com/alisterburt))

**Merged pull requests:**

- Fix typo in Nested Viewbox name in example [\#2321](https://github.com/vispy/vispy/pull/2321) ([jawjay](https://github.com/jawjay))
- Expand docs on panzoom rect setter [\#2317](https://github.com/vispy/vispy/pull/2317) ([dstansby](https://github.com/dstansby))
- Cleanup debug logic in line draw example [\#2306](https://github.com/vispy/vispy/pull/2306) ([olinickalls](https://github.com/olinickalls))

## [v0.9.6](https://github.com/vispy/vispy/tree/v0.9.6) (2022-02-04)

**Fixed bugs:**

- Fix TypeError for membership test of KeyboardModifiers [\#2293](https://github.com/vispy/vispy/pull/2293) ([rayg-ssec](https://github.com/rayg-ssec))

## [v0.9.5](https://github.com/vispy/vispy/tree/v0.9.5) (2022-02-04)

**Fixed bugs:**

- Set depth buffer in Volume plane rendering [\#2289](https://github.com/vispy/vispy/pull/2289) ([brisvag](https://github.com/brisvag))
- Fix numpy error with array edge\_width in Markers [\#2285](https://github.com/vispy/vispy/pull/2285) ([brisvag](https://github.com/brisvag))
- Fix touch event handling issue for Qt6-based backends [\#2284](https://github.com/vispy/vispy/pull/2284) ([mars0001](https://github.com/mars0001))
- remove utf-8 encode in \_vispy\_set\_title [\#2269](https://github.com/vispy/vispy/pull/2269) ([Llewyllen](https://github.com/Llewyllen))

**Merged pull requests:**

- MNT: add documentation of usage of Triangle/triangle, see \#1029 [\#2268](https://github.com/vispy/vispy/pull/2268) ([kmuehlbauer](https://github.com/kmuehlbauer))
- Add typing to `create_visual_node` [\#2264](https://github.com/vispy/vispy/pull/2264) ([tlambert03](https://github.com/tlambert03))

## [v0.9.4](https://github.com/vispy/vispy/tree/v0.9.4) (2021-11-24)

**Fixed bugs:**

- Fix MeshNormals and WireframeFilter with empty MeshData [\#2262](https://github.com/vispy/vispy/pull/2262) ([brisvag](https://github.com/brisvag))
- Update clims in color transform whenever texture.\_data\_limits changes [\#2245](https://github.com/vispy/vispy/pull/2245) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- Clarified docstring for ArrowVisual [\#2261](https://github.com/vispy/vispy/pull/2261) ([pauljurczak](https://github.com/pauljurczak))
- Use stacklevel in DeprecationWarnings. [\#2257](https://github.com/vispy/vispy/pull/2257) ([Carreau](https://github.com/Carreau))
- Add optional dependencies section to installation instructions [\#2251](https://github.com/vispy/vispy/pull/2251) ([pauljurczak](https://github.com/pauljurczak))
- Add table for list of backend supported [\#2246](https://github.com/vispy/vispy/pull/2246) ([anirudhbagri](https://github.com/anirudhbagri))

## [v0.9.3](https://github.com/vispy/vispy/tree/v0.9.3) (2021-10-27)

**Fixed bugs:**

- Noop on clicking both mouse buttons [\#2244](https://github.com/vispy/vispy/pull/2244) ([brisvag](https://github.com/brisvag))
- Fix performance issues with 0.9.1 [\#2243](https://github.com/vispy/vispy/pull/2243) ([brisvag](https://github.com/brisvag))
- Remove unnecessary if clauses from Volume [\#2242](https://github.com/vispy/vispy/pull/2242) ([brisvag](https://github.com/brisvag))
- Fix volume rendering's wrong offset [\#2239](https://github.com/vispy/vispy/pull/2239) ([brisvag](https://github.com/brisvag))
- Update PlanesClipper interpolation to occur in the fragment shader [\#2226](https://github.com/vispy/vispy/pull/2226) ([brisvag](https://github.com/brisvag))

**Merged pull requests:**

- Include tutorial image from vispy/images to remove remote reference [\#2240](https://github.com/vispy/vispy/pull/2240) ([draco2003](https://github.com/draco2003))

## [v0.9.2](https://github.com/vispy/vispy/tree/v0.9.2) (2021-10-21)

**Fixed bugs:**

- Fix colorbar orientation [\#2238](https://github.com/vispy/vispy/pull/2238) ([Dive576](https://github.com/Dive576))

## [v0.9.1](https://github.com/vispy/vispy/tree/v0.9.1) (2021-10-20)

**Merged pull requests:**

- Documentation for third party projects [\#2235](https://github.com/vispy/vispy/pull/2235) ([Dive576](https://github.com/Dive576))
- Remove "Jupyter Widget" section part [\#2233](https://github.com/vispy/vispy/pull/2233) ([djhoese](https://github.com/djhoese))
- Move module globals to class attributes [\#2227](https://github.com/vispy/vispy/pull/2227) ([brisvag](https://github.com/brisvag))

## [v0.9.0](https://github.com/vispy/vispy/tree/v0.9.0) (2021-09-29)

**Enhancements:**

- Spherical \(3D-looking\) `Markers` symbols [\#2209](https://github.com/vispy/vispy/pull/2209) ([brisvag](https://github.com/brisvag))
- Add PlanesClipper filter for visually clipping visuals by a 2D plane [\#2197](https://github.com/vispy/vispy/pull/2197) ([brisvag](https://github.com/brisvag))
- Add skinny cross marker \(++\) to MarkersVisual [\#2193](https://github.com/vispy/vispy/pull/2193) ([mars0001](https://github.com/mars0001))
- Improve depth handling for VolumeVisual iso rendering [\#2190](https://github.com/vispy/vispy/pull/2190) ([kevinyamauchi](https://github.com/kevinyamauchi))

**Fixed bugs:**

- Fix integer division when creating directed graphs [\#2223](https://github.com/vispy/vispy/pull/2223) ([Maks1mS](https://github.com/Maks1mS))
- Cleanup some refs to webgl [\#2217](https://github.com/vispy/vispy/pull/2217) ([almarklein](https://github.com/almarklein))
- Fix key event handling in Tk backend [\#2205](https://github.com/vispy/vispy/pull/2205) ([matthiasverstraete](https://github.com/matthiasverstraete))

**Merged pull requests:**

- Fix "Edit this page" links for API docs [\#2220](https://github.com/vispy/vispy/pull/2220) ([djhoese](https://github.com/djhoese))

## [v0.8.1](https://github.com/vispy/vispy/tree/v0.8.1) (2021-08-27)

**Fixed bugs:**

- Fix PyQt5 backend gesture event handling [\#2202](https://github.com/vispy/vispy/pull/2202) ([djhoese](https://github.com/djhoese))
- Fix PinchGesture attribute error on pyqt6 [\#2200](https://github.com/vispy/vispy/pull/2200) ([tlambert03](https://github.com/tlambert03))
- Fix PyQt scaling issue [\#2189](https://github.com/vispy/vispy/pull/2189) ([mars0001](https://github.com/mars0001))

**Merged pull requests:**

- Ditch example symlinks [\#2181](https://github.com/vispy/vispy/pull/2181) ([almarklein](https://github.com/almarklein))

## [v0.8.0](https://github.com/vispy/vispy/tree/v0.8.0) (2021-08-20)

**Enhancements:**

- Add PyQt6 backend [\#2172](https://github.com/vispy/vispy/pull/2172) ([mars0001](https://github.com/mars0001))
- Remove 'VNC' backend [\#2164](https://github.com/vispy/vispy/pull/2164) ([almarklein](https://github.com/almarklein))
- Refactor texture\_lut\(\) Colormap method to BaseColormap for cleaner usage [\#2160](https://github.com/vispy/vispy/pull/2160) ([almarklein](https://github.com/almarklein))
- Rendering arbitrary planes in the `VolumeVisual` [\#2149](https://github.com/vispy/vispy/pull/2149) ([alisterburt](https://github.com/alisterburt))
- Switch examples and website gallery to sphinx-gallery [\#2148](https://github.com/vispy/vispy/pull/2148) ([djhoese](https://github.com/djhoese))
- Add "jupyter\_rfb" backend for inline Jupyter Notebook/Lab display [\#2142](https://github.com/vispy/vispy/pull/2142) ([almarklein](https://github.com/almarklein))
- Migrate from string formatting to template \($\) variables in VolumeVisual shaders [\#2117](https://github.com/vispy/vispy/pull/2117) ([brisvag](https://github.com/brisvag))
- Add clipping planes to `VolumeVisual` [\#2116](https://github.com/vispy/vispy/pull/2116) ([brisvag](https://github.com/brisvag))

**Fixed bugs:**

- Fix volume\_plane.py example not having a toggle for the animation [\#2179](https://github.com/vispy/vispy/pull/2179) ([djhoese](https://github.com/djhoese))
- Fix minor bug in volume\_clipping.py example [\#2175](https://github.com/vispy/vispy/pull/2175) ([kevinyamauchi](https://github.com/kevinyamauchi))

## [v0.7.3](https://github.com/vispy/vispy/tree/v0.7.3) (2021-07-21)

**Fixed bugs:**

- Fix `VolumeVisual.cmap` setter not working for most colormaps [\#2150](https://github.com/vispy/vispy/pull/2150) ([alisterburt](https://github.com/alisterburt))

## [v0.7.2](https://github.com/vispy/vispy/tree/v0.7.2) (2021-07-20)

**Fixed bugs:**

- Add filter keyword arguments to subclassed filters [\#2144](https://github.com/vispy/vispy/pull/2144) ([clarebcook](https://github.com/clarebcook))
- Fix scalable textures clim\_normalized when auto clims are used [\#2140](https://github.com/vispy/vispy/pull/2140) ([djhoese](https://github.com/djhoese))

## [v0.7.1](https://github.com/vispy/vispy/tree/v0.7.1) (2021-07-13)

**Fixed bugs:**

- Fix auto clim calculation if all data is non-finite [\#2131](https://github.com/vispy/vispy/pull/2131) ([almarklein](https://github.com/almarklein))
- Update light direction in mesh shading examples [\#2125](https://github.com/vispy/vispy/pull/2125) ([asnt](https://github.com/asnt))

**Merged pull requests:**

- Set stacklevel for colormap deprecation. [\#2134](https://github.com/vispy/vispy/pull/2134) ([Carreau](https://github.com/Carreau))
- Make meshes upright and face the camera in mesh examples [\#2126](https://github.com/vispy/vispy/pull/2126) ([asnt](https://github.com/asnt))

## [v0.7.0](https://github.com/vispy/vispy/tree/v0.7.0) (2021-06-30)

**Enhancements:**

- Change Visual GL state so it is only set if drawing [\#2111](https://github.com/vispy/vispy/pull/2111) ([djhoese](https://github.com/djhoese))
- Add handling of NaNs in ImageVisual [\#2106](https://github.com/vispy/vispy/pull/2106) ([djhoese](https://github.com/djhoese))
- Improve specular light in phong shading [\#2091](https://github.com/vispy/vispy/pull/2091) ([almarklein](https://github.com/almarklein))
- Fix SceneCanvas Node leaking reference to itself [\#2089](https://github.com/vispy/vispy/pull/2089) ([djhoese](https://github.com/djhoese))
- Improve infinity/NaN handling in VolumeVisual and ImageVisual clim calculations [\#2085](https://github.com/vispy/vispy/pull/2085) ([almarklein](https://github.com/almarklein))
- Change builtin colormaps to all be instances [\#2066](https://github.com/vispy/vispy/pull/2066) ([djhoese](https://github.com/djhoese))
- Add setter for colorbar label text [\#2057](https://github.com/vispy/vispy/pull/2057) ([djhoese](https://github.com/djhoese))
- Add average intensity projection \(average\) rendering mode to `VolumeVisual` [\#2055](https://github.com/vispy/vispy/pull/2055) ([alisterburt](https://github.com/alisterburt))
- Add attenuated MIP \(attenuated\_mip\) rendering mode to `VolumeVisual` [\#2047](https://github.com/vispy/vispy/pull/2047) ([alisterburt](https://github.com/alisterburt))
- Add minimum intensity projection \(minip\) shading to `VolumeVisual` [\#2046](https://github.com/vispy/vispy/pull/2046) ([alisterburt](https://github.com/alisterburt))
- Add more options to control the length of normals in MeshNormals visual [\#2043](https://github.com/vispy/vispy/pull/2043) ([asnt](https://github.com/asnt))
- Add visual for displaying mesh normals [\#2031](https://github.com/vispy/vispy/pull/2031) ([asnt](https://github.com/asnt))
- Identify and expose Phong shading parameters in mesh ShadingFilter [\#2029](https://github.com/vispy/vispy/pull/2029) ([asnt](https://github.com/asnt))
- Add the ability to make the wireframe transparent with the wireframe filter [\#2026](https://github.com/vispy/vispy/pull/2026) ([asnt](https://github.com/asnt))
- Add ability to show only a mesh wireframe with the wireframe filter [\#2025](https://github.com/vispy/vispy/pull/2025) ([asnt](https://github.com/asnt))
- Optimize SurfacePlotVisual when only color is updated [\#2002](https://github.com/vispy/vispy/pull/2002) ([djhoese](https://github.com/djhoese))
- Add PySide6 backend [\#1978](https://github.com/vispy/vispy/pull/1978) ([Kusefiru](https://github.com/Kusefiru))
- Add networkx layout to GraphVisual [\#1941](https://github.com/vispy/vispy/pull/1941) ([cvanelteren](https://github.com/cvanelteren))
- Overhaul vispy website [\#1931](https://github.com/vispy/vispy/pull/1931) ([djhoese](https://github.com/djhoese))
- Add 'texture\_format' kwarg to ImageVisual for floating point textures [\#1920](https://github.com/vispy/vispy/pull/1920) ([djhoese](https://github.com/djhoese))
- Add Tkinter backend [\#1918](https://github.com/vispy/vispy/pull/1918) ([ThenTech](https://github.com/ThenTech))
- Add 'texture\_format' kwarg to VolumeVisual for floating point textures [\#1912](https://github.com/vispy/vispy/pull/1912) ([djhoese](https://github.com/djhoese))
- Let camera link be limited to specified properties [\#1886](https://github.com/vispy/vispy/pull/1886) ([povik](https://github.com/povik))
- Speed up arcball and turntable cameras [\#1884](https://github.com/vispy/vispy/pull/1884) ([povik](https://github.com/povik))
- Fix jupyter lab extension to use newest vispy.js [\#1866](https://github.com/vispy/vispy/pull/1866) ([mjlbach](https://github.com/mjlbach))
- Allow for 2D X and Y coordinates in SurfacePlotVisual [\#1863](https://github.com/vispy/vispy/pull/1863) ([dvsphanindra](https://github.com/dvsphanindra))
- Add ImageVisual gamma and smarter in-shader contrast limits [\#1844](https://github.com/vispy/vispy/pull/1844) ([tlambert03](https://github.com/tlambert03))
- Implement volume contrast limits in shader, add gamma [\#1842](https://github.com/vispy/vispy/pull/1842) ([tlambert03](https://github.com/tlambert03))
- Make demos easier to switch to PySide2 from PyQt5 [\#1835](https://github.com/vispy/vispy/pull/1835) ([fedepell](https://github.com/fedepell))
- Use meshio fall back for reading and writing mesh files [\#1824](https://github.com/vispy/vispy/pull/1824) ([nschloe](https://github.com/nschloe))
- Add nearest interpolation to volume visual [\#1803](https://github.com/vispy/vispy/pull/1803) ([sofroniewn](https://github.com/sofroniewn))
- Remove isosurface green color in VolumeVisual [\#1802](https://github.com/vispy/vispy/pull/1802) ([sofroniewn](https://github.com/sofroniewn))
- Add "transparent" color to internal color\_dict [\#1794](https://github.com/vispy/vispy/pull/1794) ([HagaiHargil](https://github.com/HagaiHargil))
- Make all AxisVisual parameters easily updatable after instantiation [\#1792](https://github.com/vispy/vispy/pull/1792) ([tlambert03](https://github.com/tlambert03))
- Make it possible to get and set the face, bold, and italic properties of Text via properties [\#1777](https://github.com/vispy/vispy/pull/1777) ([astrofrog](https://github.com/astrofrog))
- Check for GUI eventloop when testing for jupyter kernel [\#1714](https://github.com/vispy/vispy/pull/1714) ([hmaarrfk](https://github.com/hmaarrfk))
- Add lines\_adjacency and line\_strip\_adjacency OpenGL primitives. [\#1705](https://github.com/vispy/vispy/pull/1705) ([proto3](https://github.com/proto3))
- Add ability to pass webGL context arguments for notebook backend canvas initialization [\#1693](https://github.com/vispy/vispy/pull/1693) ([klarh](https://github.com/klarh))
- Add mesh wireframe filter [\#1689](https://github.com/vispy/vispy/pull/1689) ([asnt](https://github.com/asnt))
- Allow changing spectrogram parameters after it has been drawn [\#1670](https://github.com/vispy/vispy/pull/1670) ([cimbi](https://github.com/cimbi))
- Fix event loop detection triggering on blocked events [\#1590](https://github.com/vispy/vispy/pull/1590) ([kne42](https://github.com/kne42))
- Replace Grid Widget cassowary solver with kiwisolver [\#1501](https://github.com/vispy/vispy/pull/1501) ([MatthieuDartiailh](https://github.com/MatthieuDartiailh))
- Add ShadingFilter for meshes by separating it from MeshVisual [\#1463](https://github.com/vispy/vispy/pull/1463) ([asnt](https://github.com/asnt))
- Refactor MeshVisual indexing for easier and more flexible filter creation [\#1462](https://github.com/vispy/vispy/pull/1462) ([asnt](https://github.com/asnt))
- Changed vispy.plot.Fig.\_\_init\_\_\(\) to allow passing 'keys' argument [\#1449](https://github.com/vispy/vispy/pull/1449) ([jimofthecorn](https://github.com/jimofthecorn))
- Add TextureFilter for adding textures to MeshVisuals [\#1444](https://github.com/vispy/vispy/pull/1444) ([asnt](https://github.com/asnt))

**Fixed bugs:**

- Fix VolumeVisual artifacts with mip/minip if nothing was found [\#2115](https://github.com/vispy/vispy/pull/2115) ([brisvag](https://github.com/brisvag))
- Fix inconsistent picking behavior regarding depth testing [\#2110](https://github.com/vispy/vispy/pull/2110) ([djhoese](https://github.com/djhoese))
- Fix grid solver not updating variables when height/width changed [\#2100](https://github.com/vispy/vispy/pull/2100) ([djhoese](https://github.com/djhoese))
- Fix alpha handling in 'translucent' Visuals and add 'alpha' keyword argument to Canvas.render [\#2090](https://github.com/vispy/vispy/pull/2090) ([djhoese](https://github.com/djhoese))
- Fix PanZoomCamera 'center' property not updating view [\#2079](https://github.com/vispy/vispy/pull/2079) ([djhoese](https://github.com/djhoese))
- Fix VolumeVisual bounds representing the wrong axis [\#2070](https://github.com/vispy/vispy/pull/2070) ([djhoese](https://github.com/djhoese))
- make agg lines write correct depth value [\#2063](https://github.com/vispy/vispy/pull/2063) ([almarklein](https://github.com/almarklein))
- Fix glfw not sizing visuals correctly on initial draw [\#2059](https://github.com/vispy/vispy/pull/2059) ([djhoese](https://github.com/djhoese))
- Dont force selection of gl2 backend [\#2058](https://github.com/vispy/vispy/pull/2058) ([almarklein](https://github.com/almarklein))
- Fix typo in double shader [\#2051](https://github.com/vispy/vispy/pull/2051) ([theGiallo](https://github.com/theGiallo))
- Fix changing mesh shading mode when initially None [\#2042](https://github.com/vispy/vispy/pull/2042) ([asnt](https://github.com/asnt))
- Prevent translucent window with QOpenGLWidget [\#2040](https://github.com/vispy/vispy/pull/2040) ([asnt](https://github.com/asnt))
- Fix various issues with shading in the MeshVisual [\#2028](https://github.com/vispy/vispy/pull/2028) ([asnt](https://github.com/asnt))
- Fix face normal in cube geometry \(create\_cube function\) [\#2027](https://github.com/vispy/vispy/pull/2027) ([asnt](https://github.com/asnt))
- Fix axis labeling issue when flipped [\#2022](https://github.com/vispy/vispy/pull/2022) ([Kusefiru](https://github.com/Kusefiru))
- Fix TextVisual producing log message about unused uniform [\#2004](https://github.com/vispy/vispy/pull/2004) ([djhoese](https://github.com/djhoese))
- Add workaround for MacOS dlopen [\#1975](https://github.com/vispy/vispy/pull/1975) ([rayg-ssec](https://github.com/rayg-ssec))
- Fix data type issue in create\_sphere\(\) [\#1956](https://github.com/vispy/vispy/pull/1956) ([desteemy](https://github.com/desteemy))
- Fix ImportError on Python 3.9 [\#1914](https://github.com/vispy/vispy/pull/1914) ([cgohlke](https://github.com/cgohlke))
- Fix ImageVisual not updating color transform after texture update [\#1911](https://github.com/vispy/vispy/pull/1911) ([tlambert03](https://github.com/tlambert03))
- Fix OpenGL to ctypes type mapping [\#1883](https://github.com/vispy/vispy/pull/1883) ([cgohlke](https://github.com/cgohlke))
- Fix ImageVisual updating vertex coordinates on every draw [\#1853](https://github.com/vispy/vispy/pull/1853) ([djhoese](https://github.com/djhoese))
- Fix GitHub raw file download base URL [\#1821](https://github.com/vispy/vispy/pull/1821) ([djhoese](https://github.com/djhoese))
- Fix LinePlotVisual not remembering styles [\#1807](https://github.com/vispy/vispy/pull/1807) ([tlambert03](https://github.com/tlambert03))
- Fix grid\_widget when Fig gets a single element [\#1101](https://github.com/vispy/vispy/pull/1101) ([gouarin](https://github.com/gouarin))

**Merged pull requests:**

- Replace CI environment variable checks with constants [\#2119](https://github.com/vispy/vispy/pull/2119) ([djhoese](https://github.com/djhoese))
- Refactor ImageVisual for easier subclassing [\#2105](https://github.com/vispy/vispy/pull/2105) ([djhoese](https://github.com/djhoese))
- Restore ambient light behavior as in v0.6.0 [\#2088](https://github.com/vispy/vispy/pull/2088) ([asnt](https://github.com/asnt))
- Document OpenGL state presets [\#2084](https://github.com/vispy/vispy/pull/2084) ([asnt](https://github.com/asnt))
- Add Code of Conduct [\#2076](https://github.com/vispy/vispy/pull/2076) ([djhoese](https://github.com/djhoese))
- Rename all HUSL usages to HSLuv [\#2061](https://github.com/vispy/vispy/pull/2061) ([djhoese](https://github.com/djhoese))
- Remove unused py2/3 compatibility module [\#2060](https://github.com/vispy/vispy/pull/2060) ([djhoese](https://github.com/djhoese))
- Fix dead link in shader docstring [\#2050](https://github.com/vispy/vispy/pull/2050) ([theGiallo](https://github.com/theGiallo))
- Fix website deploy commit message references [\#2038](https://github.com/vispy/vispy/pull/2038) ([djhoese](https://github.com/djhoese))
- Fix URL to contributor guide [\#2032](https://github.com/vispy/vispy/pull/2032) ([asnt](https://github.com/asnt))
- Fixed multiple code style issues. [\#1983](https://github.com/vispy/vispy/pull/1983) ([Aaru143](https://github.com/Aaru143))
- Removed Python 2.7 wrapper on GzipFile [\#1943](https://github.com/vispy/vispy/pull/1943) ([irajasyed](https://github.com/irajasyed))
- Replaced bundled 'pypng' \(png\) dependency with pillow [\#1934](https://github.com/vispy/vispy/pull/1934) ([Kartik-byte](https://github.com/Kartik-byte))
- Remove six dependency [\#1933](https://github.com/vispy/vispy/pull/1933) ([sgaist](https://github.com/sgaist))
- Fix typo in examples/basics/gloo/hello\_fbo.py  [\#1930](https://github.com/vispy/vispy/pull/1930) ([BioGeek](https://github.com/BioGeek))
- Fix EGL docstring copy/paste error [\#1921](https://github.com/vispy/vispy/pull/1921) ([BioGeek](https://github.com/BioGeek))
- Fix various numpy deprecation warnings [\#1913](https://github.com/vispy/vispy/pull/1913) ([GuillaumeFavelier](https://github.com/GuillaumeFavelier))
- Fix styling issues due to new flake8 version [\#1864](https://github.com/vispy/vispy/pull/1864) ([djhoese](https://github.com/djhoese))
- Update vispy.js submodule to 0.3.0 [\#1837](https://github.com/vispy/vispy/pull/1837) ([djhoese](https://github.com/djhoese))
- Fix DataBuffer.set\_subdata docstring with wrong offset units [\#1825](https://github.com/vispy/vispy/pull/1825) ([asnt](https://github.com/asnt))
- DOC: Drop installation instructions from readme [\#1806](https://github.com/vispy/vispy/pull/1806) ([hoechenberger](https://github.com/hoechenberger))
- Add new example for mouse editing/drawing of shapes [\#1480](https://github.com/vispy/vispy/pull/1480) ([fschill](https://github.com/fschill))

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
