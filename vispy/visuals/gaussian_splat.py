# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""A visual for rendering 3D Gaussian Splatting scenes."""

import numpy as np

from .. import gloo
from .visual import Visual

# per-splat records (16 floats = 4 RGBA32F texels) are stored in a data texture
# and fetched in the vertex shader by index; only the sorted index order is
# re-uploaded per frame
# splat n occupies linear texels [n*4 : n*4+4]
# texture is a fixed width and grows in height with the splat count
# indices stay exact in float32 up to ~2**24 splats, so that's the max
_SPLATS_PER_ROW = 1024
_TEXELS_PER_SPLAT = 4
_TEX_WIDTH = _SPLATS_PER_ROW * _TEXELS_PER_SPLAT
_MAX_TEX_HEIGHT = 16384
_MAX_SPLATS = _SPLATS_PER_ROW * _MAX_TEX_HEIGHT


VERTEX_SHADER = """
attribute vec2 a_quad;      // per-vertex: quad corner in [-1, 1]
attribute float a_index;    // per-instance: splat index to fetch and draw

uniform sampler2D u_splats; // static per-splat data (RGBA32F)
uniform vec2 u_tex_size;    // data texture size in texels (width, height)
uniform float u_per_row;    // splats per texture row

uniform float u_eps;        // finite-difference step (visual units)

const float c_cutoff = 3.0;    // quad half-extent in sigmas
const float c_dilation = 0.3;  // low-pass dilation added to screen cov (px^2)

varying vec4 v_color;
varying vec2 v_offset;      // pixel offset from center at this vertex
varying vec3 v_conic;       // inverse screen covariance: c00, c01, c11

vec4 fetch(float col, float row) {
    // nearest sampling; +0.5 centers the sample on the texel
    vec2 uv = (vec2(col, row) + 0.5) / u_tex_size;
    return texture2D(u_splats, uv);
}

vec2 project(vec3 p) {
    vec4 fb = $visual_to_framebuffer(vec4(p, 1.0));
    return fb.xy / fb.w;
}

void main() {
    // locate this splat's 4 texels and unpack its record
    float row = floor(a_index / u_per_row);
    float col0 = (a_index - row * u_per_row) * 4.0;
    vec4 t0 = fetch(col0, row);
    vec4 t1 = fetch(col0 + 1.0, row);
    vec4 t2 = fetch(col0 + 2.0, row);
    vec4 t3 = fetch(col0 + 3.0, row);

    vec3 a_center = t0.xyz;
    vec3 a_cov_a = vec3(t0.w, t1.x, t1.y);   // Sigma00, Sigma01, Sigma02
    vec3 a_cov_b = vec3(t1.z, t1.w, t2.x);   // Sigma11, Sigma12, Sigma22
    vec4 a_color = vec4(t2.yzw, t3.x);       // rgba

    vec4 fb_center = $visual_to_framebuffer(vec4(a_center, 1.0));
    vec2 c = fb_center.xy / fb_center.w;

    // finite-difference Jacobian J (2x3)
    // get visual-space displacement -> pixels for each dim
    vec2 jx = (project(a_center + vec3(u_eps, 0.0, 0.0)) - c) / u_eps;
    vec2 jy = (project(a_center + vec3(0.0, u_eps, 0.0)) - c) / u_eps;
    vec2 jz = (project(a_center + vec3(0.0, 0.0, u_eps)) - c) / u_eps;

    mat3 sigma = mat3(
        a_cov_a.x, a_cov_a.y, a_cov_a.z,
        a_cov_a.y, a_cov_b.x, a_cov_b.y,
        a_cov_a.z, a_cov_b.y, a_cov_b.z
    );

    // screen covariance Sigma2 = J Sigma J^T (2x2)
    // r0, r1 are rows of J
    vec3 r0 = vec3(jx.x, jy.x, jz.x);
    vec3 r1 = vec3(jx.y, jy.y, jz.y);
    vec3 sr0 = sigma * r0;
    vec3 sr1 = sigma * r1;
    float ca = dot(r0, sr0) + c_dilation;   // Sigma2_00
    float cb = dot(r0, sr1);                // Sigma2_01
    float cc = dot(r1, sr1) + c_dilation;   // Sigma2_11

    float det = ca * cc - cb * cb;
    if (det <= 0.0) {
        // degenerate splat
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
        return;
    }

    // inverse screen covariance (conic), passed to the fragment shader
    v_conic = vec3(cc, -cb, ca) / det;

    // eigen-decomposition of the symmetric 2x2 to size/orient the quad
    float tr = ca + cc;
    float disc = sqrt(max(tr * tr * 0.25 - det, 0.0));
    float l1 = tr * 0.5 + disc;
    float l2 = max(tr * 0.5 - disc, 0.0);
    vec2 e1;
    if (abs(cb) < 1e-9) {
        e1 = (ca >= cc) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    } else {
        e1 = normalize(vec2(l1 - cc, cb));
    }
    vec2 e2 = vec2(-e1.y, e1.x);
    float r_major = c_cutoff * sqrt(l1);
    float r_minor = c_cutoff * sqrt(l2);

    vec2 offset = a_quad.x * r_major * e1 + a_quad.y * r_minor * e2;  // pixels

    v_offset = offset;
    v_color = a_color;

    // offset is in true (post-divide) pixels, but framebuffer coords are
    // pre-perspective-divide, so scale by w
    // the GPU's later /w then yields the intended pixel offset
    // no-op under orthographic (w == 1)
    vec4 fb = fb_center;
    fb.xy += offset * fb.w;
    gl_Position = $framebuffer_to_render(fb);
}
"""

FRAGMENT_SHADER = """
varying vec4 v_color;
varying vec2 v_offset;
varying vec3 v_conic;

void main() {
    vec2 o = v_offset;
    float power = -0.5 * (
        v_conic.x * o.x * o.x
        + 2.0 * v_conic.y * o.x * o.y
        + v_conic.z * o.y * o.y
    );

    if (power > 0.0)
        discard;

    float alpha = v_color.a * exp(power);

    if (alpha < 1.0 / 255.0)
        discard;

    // premultiplied "over" blending
    gl_FragColor = vec4(v_color.rgb * alpha, alpha);
}
"""


class GaussianSplatVisual(Visual):
    """Renderer for a 3D Gaussian Splatting scene.

    Each Gaussian ("splat") is defined by a center, a 3x3 covariance matrix,
    and an RGBA color. Each is drawn as an instanced screen-aligned
    (billboarded) quad - similar to the instanced Markers visual.

    The 3D covariance is projected to a 2D screen-space covariance in the
    vertex shader using a finite-difference Jacobian of the visual->framebuffer
    projection (the vispy equivalent of the model-view-projection). Finite
    differences are used because that projection is nonlinear under a
    perspective camera. The fragment shader evaluates the resulting 2D
    Gaussian. Splats are sorted and rendered back-to-front and blended (no
    depth testing).

    Parameters
    ----------
    positions : (N, 3) array
        Gaussian centers, in visual coordinates.
    covariances : (N, 3, 3) array
        Symmetric positive-definite 3D covariance matrix for each Gaussian.
    colors : (N, 4) array
        RGBA color for each Gaussian, in [0, 1]. The alpha channel is the
        Gaussian's peak opacity.

    Notes
    -----
    Per-splat records are stored once in a data texture and fetched in the
    vertex shader by index. The splats are depth-sorted on the CPU, but only
    the (N,) index order is re-uploaded, and only when the view *direction*
    rotates (pan, zoom and static redraws reuse the existing order) -- so the
    heavy per-splat data never moves after upload, which keeps interaction
    smooth for up to a few million splats.

    Color is a fixed per-Gaussian RGBA value; view-dependent color is often
    included in splat data, but yet not supported here.
    """

    def __init__(self, positions, covariances, colors):
        Visual.__init__(self, VERTEX_SHADER, FRAGMENT_SHADER)

        self._splat_pos = None
        self._splat_cov_a = None
        self._splat_cov_b = None
        self._splat_rgba = None

        # cached bounding box, rows (min, max), for _compute_bounds
        self._bounds = None

        # view direction (normalized framebuffer-depth gradient) at the last
        # sort; the order only changes when this rotates, so _sort skips pan,
        # zoom and static redraws (see _sort).
        self._last_view_dir = None

        # instancing quad, drawn as a triangle strip
        quad = np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype=np.float32)
        self.shared_program["a_quad"] = gloo.VertexBuffer(quad)

        # per-instance draw order (splat indices, far -> near)
        # reuploaded on _sort
        self._index_vbo = gloo.VertexBuffer(np.zeros(1, np.float32), divisor=1)
        self.shared_program["a_index"] = self._index_vbo

        # static per-splat data texture
        self._tex = gloo.Texture2D(
            np.zeros((1, _TEX_WIDTH, 4), np.float32),
            interpolation="nearest",
            internalformat="rgba32f",
        )
        self.shared_program["u_splats"] = self._tex
        self.shared_program["u_per_row"] = float(_SPLATS_PER_ROW)
        self.shared_program["u_tex_size"] = (float(_TEX_WIDTH), 1.0)

        self._draw_mode = "triangle_strip"

        # premultiplied "over" blending, sort back-to-front on the CPU (_sort)
        self.set_gl_state(
            depth_test=False,
            cull_face=False,
            blend=True,
            blend_func=("one", "one_minus_src_alpha"),
        )

        self.set_data(positions, covariances, colors)

    @property
    def positions(self):
        """The (N, 3) array of Gaussian centers."""
        return self._splat_pos

    @property
    def covariances(self):
        """The (N, 3, 3) array of per-Gaussian 3D covariance matrices."""
        a, b = self._splat_cov_a, self._splat_cov_b
        sigma = np.zeros((len(a), 3, 3), dtype=np.float32)
        # cov_a = (S00, S01, S02), cov_b = (S11, S12, S22).
        sigma[:, 0, 0], sigma[:, 0, 1], sigma[:, 0, 2] = a[:, 0], a[:, 1], a[:, 2]
        sigma[:, 1, 1], sigma[:, 1, 2], sigma[:, 2, 2] = b[:, 0], b[:, 1], b[:, 2]
        # mirror to the lower triangle
        sigma[:, 1, 0], sigma[:, 2, 0], sigma[:, 2, 1] = a[:, 1], a[:, 2], b[:, 1]
        return sigma

    @property
    def colors(self):
        """The (N, 4) array of per-Gaussian RGBA colors."""
        return self._splat_rgba

    def set_data(self, positions=None, covariances=None, colors=None):
        """Update any subset of the per-Gaussian data arrays.

        Parameters not supplied are left unchanged. See the class docstring
        for the expected shapes.
        """
        if positions is not None:
            pos = np.ascontiguousarray(positions, dtype=np.float32)
            if pos.ndim != 2 or pos.shape[1] != 3:
                raise ValueError(f"positions must have shape (N, 3), got {pos.shape}")
            self._splat_pos = pos
            lo, hi = pos.min(0), pos.max(0)
            self._bounds = np.array([lo, hi], dtype=np.float32)
            # finite-difference step: ~1% of the largest bounding-box side, so
            # it stays numerically well-conditioned whatever the data's units
            extent = float((hi - lo).max())
            self.shared_program["u_eps"] = 1e-2 * extent if extent > 0 else 1e-2
        if covariances is not None:
            cov = np.asarray(covariances, dtype=np.float32)
            if cov.ndim != 3 or cov.shape[1:] != (3, 3):
                raise ValueError(
                    f"covariances must have shape (N, 3, 3), got {cov.shape}"
                )
            # pack the symmetric 3x3 as cov_a=(S00,S01,S02), cov_b=(S11,S12,S22)
            self._splat_cov_a = np.ascontiguousarray(cov[:, 0, :])
            self._splat_cov_b = np.ascontiguousarray(
                np.stack([cov[:, 1, 1], cov[:, 1, 2], cov[:, 2, 2]], axis=-1)
            )
        if colors is not None:
            rgba = np.ascontiguousarray(colors, dtype=np.float32)
            if rgba.ndim != 2 or rgba.shape[1] != 4:
                raise ValueError(
                    f"colors must have shape (N, 4) RGBA, got {rgba.shape}"
                )
            self._splat_rgba = rgba

        # update the data texture from the current arrays, then force a
        # re-sort (which re-uploads the index order) on the next draw
        self._pack_texture()
        self._last_view_dir = None
        self.update()

    def _pack_texture(self):
        """Pack the per-splat records into the data texture (uploaded once per
        data change; the sort only re-uploads indices)."""
        pos = self._splat_pos
        cov_a, cov_b, rgba = self._splat_cov_a, self._splat_cov_b, self._splat_rgba
        m = len(pos)
        if not (len(cov_a) == m and len(cov_b) == m and len(rgba) == m):
            raise ValueError(
                "positions, covariances and colors must have matching lengths"
            )
        if m > _MAX_SPLATS:
            raise ValueError(
                f"GaussianSplatVisual supports at most {_MAX_SPLATS} splats, "
                f"got {m}"
            )

        # 16 floats (4 RGBA texels) per splat; splat i -> linear texels [i*4:].
        packed = np.zeros((m, _TEXELS_PER_SPLAT, 4), np.float32)
        packed[:, 0, 0:3] = pos
        packed[:, 0, 3] = cov_a[:, 0]                 # S00
        packed[:, 1, 0] = cov_a[:, 1]                 # S01
        packed[:, 1, 1] = cov_a[:, 2]                 # S02
        packed[:, 1, 2] = cov_b[:, 0]                 # S11
        packed[:, 1, 3] = cov_b[:, 1]                 # S12
        packed[:, 2, 0] = cov_b[:, 2]                 # S22
        packed[:, 2, 1:4] = rgba[:, :3]               # rgb
        packed[:, 3, 0] = rgba[:, 3]                  # a

        height = int(np.ceil(m / _SPLATS_PER_ROW))
        tex = np.zeros((height, _TEX_WIDTH, 4), np.float32)
        tex.reshape(-1, 4)[: m * _TEXELS_PER_SPLAT] = packed.reshape(-1, 4)
        self._tex.set_data(tex)
        self.shared_program["u_tex_size"] = (float(_TEX_WIDTH), float(height))

    def _depth_gradient(self, view):
        """Gradient of framebuffer depth w.r.t. position (the view axis).

        The visual->framebuffer chain is affine, so framebuffer z is a linear
        function of position; four probes recover its gradient. ``pos @ grad``
        is then a back-to-front sort key that needs no per-point projective map
        or perspective divide, and its direction is the view axis used to
        decide when a re-sort is actually needed.
        """
        tr = view.get_transform("visual", "framebuffer")
        probes = np.array(
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32
        )
        z = tr.map(probes)[:, 2]
        return (z[1:] - z[0]).astype(np.float32)  # d(depth)/d(x, y, z)

    def _sort(self, view):
        """Re-sort and re-upload the draw order if view direction changes."""
        grad = self._depth_gradient(view)
        norm = np.linalg.norm(grad)
        if norm == 0:
            return
        view_dir = grad / norm
        if self._last_view_dir is not None and np.allclose(
            view_dir, self._last_view_dir
        ):
            return
        self._last_view_dir = view_dir

        depth = self._splat_pos @ grad
        lo, hi = float(depth.min()), float(depth.max())
        if hi > lo:
            # quantize to uint16 so the stable argsort is an O(N) radix sort;
            key = ((hi - depth) * (65535.0 / (hi - lo))).astype(np.uint16)
            order = np.argsort(key, kind="stable").astype(np.float32)
        else:
            # all splats share a depth plane: any order composites the same
            order = np.arange(len(depth), dtype=np.float32)

        self._index_vbo.set_data(order)

    def _prepare_draw(self, view):
        if self._splat_pos is None or len(self._splat_pos) == 0:
            return False
        self._sort(view)
        return True

    def _prepare_transforms(self, view):
        prog = view.view_program
        prog.vert["visual_to_framebuffer"] = view.get_transform("visual", "framebuffer")
        prog.vert["framebuffer_to_render"] = view.get_transform("framebuffer", "render")

    def _compute_bounds(self, axis, view):
        if self._bounds is None:
            return None
        return self._bounds[0, axis], self._bounds[1, axis]
