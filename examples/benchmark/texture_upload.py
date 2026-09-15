#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Benchmark synchronous 2D and 3D texture sub-uploads.

The benchmark updates progressively larger regions of preallocated textures
and measures the draw that submits each upload. A ``glFinish`` is included so
timings are comparable across OpenGL drivers that otherwise enqueue work
asynchronously. The window displays the sampled 2D and 3D textures while the
benchmark runs.

Run ``python examples/benchmark/texture_upload.py --help`` for options.
"""

import argparse
import math
import platform
import statistics
import time

import numpy as np

import vispy
from vispy import app, gloo


VERT_SHADER = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main()
{
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""


FRAG_SHADER_2D = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;

void main()
{
    float value = texture2D(u_texture, v_texcoord).r;
    gl_FragColor = vec4(value, value, value, 1.0);
}
"""


FRAG_SHADER_3D = """
uniform sampler3D u_texture;
uniform float u_depth;
varying vec2 v_texcoord;

void main()
{
    float value = texture3D(u_texture,
                            vec3(v_texcoord, u_depth)).r;
    gl_FragColor = vec4(value, value, value, 1.0);
}
"""


def _upload_shape(ndim, size_mib, row_width):
    """Return a uint8 upload shape containing at least *size_mib*."""
    requested_bytes = size_mib * 2**20
    if ndim == 2:
        return (math.ceil(requested_bytes / row_width), row_width)
    plane_size = row_width**2
    return (math.ceil(requested_bytes / plane_size), row_width, row_width)


def _quad(left, right):
    positions = np.array(
        [[left, -1], [right, -1], [left, 1], [right, 1]],
        dtype=np.float32,
    )
    texcoords = np.array(
        [[0, 0], [1, 0], [0, 1], [1, 1]],
        dtype=np.float32,
    )
    return positions, texcoords


class TextureUploadBenchmark(app.Canvas):
    """Display and time a sequence of texture sub-uploads."""

    def __init__(
        self,
        sizes_mib,
        repeats,
        warmups,
        texture_2d_width,
        texture_3d_width,
    ):
        super().__init__(
            keys='interactive',
            size=(1000, 600),
            title='2D and 3D texture upload benchmark',
        )

        widths = {2: texture_2d_width, 3: texture_3d_width}
        self._shapes = {
            (ndim, size): _upload_shape(ndim, size, widths[ndim])
            for ndim in (2, 3)
            for size in sizes_mib
        }
        texture_shapes = {
            ndim: self._shapes[(ndim, sizes_mib[-1])]
            for ndim in (2, 3)
        }
        self._textures = {
            2: gloo.Texture2D(
                np.zeros(texture_shapes[2], dtype=np.uint8),
                interpolation='nearest',
                wrapping='clamp_to_edge',
            ),
            3: gloo.Texture3D(
                np.zeros(texture_shapes[3], dtype=np.uint8),
                interpolation='nearest',
                wrapping='clamp_to_edge',
            ),
        }
        self._programs = self._create_programs()

        largest = sizes_mib[-1]
        self._tasks = [
            (False, ndim, largest)
            for ndim in (2, 3)
            for _ in range(warmups)
        ] + [
            (True, ndim, size)
            for ndim in (2, 3)
            for size in sizes_mib
            for _ in range(repeats)
        ]
        self._samples = {
            (ndim, size): []
            for ndim in (2, 3)
            for size in sizes_mib
        }
        self._texture_shapes = texture_shapes
        self._payload = None
        self._payload_key = None
        self._pending = None
        self.show()

    def _create_programs(self):
        programs = {
            2: gloo.Program(VERT_SHADER, FRAG_SHADER_2D),
            3: gloo.Program(VERT_SHADER, FRAG_SHADER_3D),
        }
        for ndim, bounds in ((2, (-1, 0)), (3, (0, 1))):
            positions, texcoords = _quad(*bounds)
            programs[ndim]['a_position'] = positions
            programs[ndim]['a_texcoord'] = texcoords
            programs[ndim]['u_texture'] = self._textures[ndim]
        programs[3]['u_depth'] = 0.5
        return programs

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        started = time.perf_counter()
        gloo.clear(color='black')
        for program in self._programs.values():
            program.draw('triangle_strip')
        gloo.finish()
        elapsed = time.perf_counter() - started

        if self._pending is not None:
            record, ndim, size = self._pending
            if record:
                self._samples[(ndim, size)].append(elapsed)
        if self._tasks:
            self._queue_next_upload()
            self.update()
        else:
            self._finish()

    def _queue_next_upload(self):
        self._pending = self._tasks.pop(0)
        _, ndim, size = self._pending
        key = (ndim, size)
        shape = self._shapes[key]
        if key != self._payload_key:
            self._payload = np.empty(shape, dtype=np.uint8)
            self._payload[...] = np.linspace(
                0, 255, shape[-1], dtype=np.uint8
            )
            self._payload_key = key

        # Change a texel so each iteration supplies distinct data.
        self._payload.flat[0] ^= 1
        texture_shape = self._texture_shapes[ndim]
        offset = ((texture_shape[0] - shape[0]) // 2,) + (0,) * (ndim - 1)
        self._textures[ndim].set_data(
            self._payload, offset=offset, copy=False
        )
        if ndim == 3:
            self._programs[3]['u_depth'] = (
                offset[0] + shape[0] / 2
            ) / texture_shape[0]

    def _finish(self):
        renderer = gloo.gl.glGetParameter(gloo.gl.GL_RENDERER)
        gl_version = gloo.gl.glGetParameter(gloo.gl.GL_VERSION)
        print(f'platform: {platform.platform()}')  # noqa: T201
        print(f'python: {platform.python_version()}')  # noqa: T201
        print(f'vispy: {vispy.__version__}; numpy: {np.__version__}')  # noqa: T201
        print(f'backend: {app.use_app().backend_name}')  # noqa: T201
        print(f'GL renderer: {renderer}')  # noqa: T201
        print(f'GL version: {gl_version}')  # noqa: T201
        print('dtype: uint8; channels: 1')  # noqa: T201
        print(  # noqa: T201
            'dim requested  actual upload shape      median      min      '
            'max throughput'
        )
        print(  # noqa: T201
            '         MiB     MiB                       ms       ms       '
            'ms      GiB/s'
        )
        for (ndim, size), samples in self._samples.items():
            shape = self._shapes[(ndim, size)]
            nbytes = math.prod(shape)
            milliseconds = [sample * 1e3 for sample in samples]
            median = statistics.median(milliseconds)
            throughput = nbytes / 2**30 / (median / 1e3)
            shape_text = 'x'.join(map(str, shape))
            print(  # noqa: T201
                f'{ndim:>2}D {size:9g} {nbytes / 2**20:7.2f} '
                f'{shape_text:<16} {median:9.2f} '
                f'{min(milliseconds):8.2f} {max(milliseconds):8.2f} '
                f'{throughput:10.2f}'
            )
        app.quit()


def _positive_int(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError('must be greater than zero')
    return value


def _parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--sizes-mib',
        nargs='+',
        type=_positive_int,
        default=[1, 2, 4, 8, 16, 32, 64],
        metavar='MIB',
        help='requested upload sizes (default: 1 2 4 8 16 32 64)',
    )
    parser.add_argument(
        '--repeats',
        type=_positive_int,
        default=5,
        help='recorded uploads per dimension and size (default: 5)',
    )
    parser.add_argument(
        '--warmups',
        type=int,
        default=2,
        help='unrecorded uploads per dimension (default: 2)',
    )
    parser.add_argument(
        '--texture-2d-width',
        type=_positive_int,
        default=8192,
        help='width of the 2D texture in texels (default: 8192)',
    )
    parser.add_argument(
        '--texture-3d-width',
        type=_positive_int,
        default=512,
        help='width and height of the 3D texture in texels (default: 512)',
    )
    args = parser.parse_args()
    if args.warmups < 0:
        parser.error('--warmups must not be negative')
    args.sizes_mib = sorted(set(args.sizes_mib))
    return args


if __name__ == '__main__':
    arguments = _parse_args()
    TextureUploadBenchmark(
        sizes_mib=arguments.sizes_mib,
        repeats=arguments.repeats,
        warmups=arguments.warmups,
        texture_2d_width=arguments.texture_2d_width,
        texture_3d_width=arguments.texture_3d_width,
    )
    app.run()
