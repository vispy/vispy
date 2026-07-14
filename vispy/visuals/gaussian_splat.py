# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""A visual for rendering 3D Gaussian Splatting scenes."""

import numpy as np

from .. import gloo
from .visual import Visual


VERTEX_SHADER = """
attribute vec2 a_quad;      // per-vertex: quad corner in [-1, 1]
attribute vec3 a_center;    // instance: gaussian center (visual coords)
attribute vec3 a_cov_a;     // instance: Sigma00, Sigma01, Sigma02
attribute vec3 a_cov_b;     // instance: Sigma11, Sigma12, Sigma22
attribute vec4 a_color;     // instance: float rgba [0, 1]

uniform float u_eps;        // finite-difference step (visual units)

const float c_cutoff = 3.0;    // quad half-extent in sigmas
const float c_dilation = 0.3;  // low-pass dilation added to screen cov (px^2)

varying vec4 v_color;
varying vec2 v_offset;      // pixel offset from center at this vertex
varying vec3 v_conic;       // inverse screen covariance: c00, c01, c11

vec2 project(vec3 p) {
    vec4 fb = $visual_to_framebuffer(vec4(p, 1.0));
    return fb.xy / fb.w;
}

void main() {
    vec4 fb_center = $visual_to_framebuffer(vec4(a_center, 1.0));
    vec2 c = fb_center.xy / fb_center.w;

    // Finite-difference Jacobian J (2x3): visual-space displacement -> pixels.
    vec2 jx = (project(a_center + vec3(u_eps, 0.0, 0.0)) - c) / u_eps;
    vec2 jy = (project(a_center + vec3(0.0, u_eps, 0.0)) - c) / u_eps;
    vec2 jz = (project(a_center + vec3(0.0, 0.0, u_eps)) - c) / u_eps;

    mat3 sigma = mat3(
        a_cov_a.x, a_cov_a.y, a_cov_a.z,
        a_cov_a.y, a_cov_b.x, a_cov_b.y,
        a_cov_a.z, a_cov_b.y, a_cov_b.z
    );

    // Screen covariance Sigma2 = J Sigma J^T (2x2). r0, r1 are rows of J.
    vec3 r0 = vec3(jx.x, jy.x, jz.x);
    vec3 r1 = vec3(jx.y, jy.y, jz.y);
    vec3 sr0 = sigma * r0;
    vec3 sr1 = sigma * r1;
    float ca = dot(r0, sr0) + c_dilation;   // Sigma2_00
    float cb = dot(r0, sr1);                // Sigma2_01
    float cc = dot(r1, sr1) + c_dilation;   // Sigma2_11

    float det = ca * cc - cb * cb;
    if (det <= 0.0) {                       // degenerate splat: cull
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
        return;
    }

    // Inverse screen covariance (conic), passed to the fragment shader.
    v_conic = vec3(cc, -cb, ca) / det;

    // Eigen-decomposition of the symmetric 2x2 to size/orient the quad.
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
    // pre-perspective-divide, so scale by w; the GPU's later /w then yields the
    // intended pixel offset. No-op under orthographic (w == 1).
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
    float power = -0.5 * (v_conic.x * o.x * o.x
                          + 2.0 * v_conic.y * o.x * o.y
                          + v_conic.z * o.y * o.y);
    if (power > 0.0)
        discard;
    float alpha = v_color.a * exp(power);
    if (alpha < 1.0 / 255.0)
        discard;
    gl_FragColor = vec4(v_color.rgb * alpha, alpha);   // premultiplied "over"
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
    perspective camera, which keeps the visual camera-agnostic. The fragment
    shader evaluates the resulting 2D Gaussian. Splats are sorted and rendered
    back-to-front and blended (no depth testing).

    Parameters
    ----------
    positions : (N, 3) array
        Gaussian centers, in visual coordinates.
    covariances : (N, 3, 3) array
        Symmetric positive-definite 3D covariance matrix for each Gaussian.
    colors : (N, 4) array
        RGBA color for each Gaussian, in [0, 1]. The alpha channel is the
        Gaussian's peak opacity.
    eps : float, optional
        Finite-difference step (in visual units) used to build the
        visual->framebuffer Jacobian in the vertex shader. The default suits
        data normalized to roughly a unit box; increase it for larger scenes.

    Notes
    -----
    The depth sort re-uploads the instance buffers whenever the camera moves,
    which is fine for up to a few million splats.

    Color is a fixed per-Gaussian RGBA value; view-dependent color is not
    supported.
    """

    def __init__(self, positions, covariances, colors, eps=1e-2):
        Visual.__init__(self, VERTEX_SHADER, FRAGMENT_SHADER)

        # NB: prefix data attributes to avoid clobbering reserved Visual
        # attributes (e.g. Visual._opacity, reset to a float by the node
        # wrapper in create_visual_node).
        self._gs_pos = None
        self._gs_cov_a = None
        self._gs_cov_b = None
        self._gs_rgba = None
        # A few probe points to cheaply detect camera changes for re-sorting.
        self._probes = None
        self._last_sig = None

        # Per-vertex quad (corners in [-1, 1]); drawn as a triangle strip.
        quad = np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype=np.float32)
        self.shared_program['a_quad'] = gloo.VertexBuffer(quad)
        self.shared_program['u_eps'] = float(eps)

        # Instanced (divisor=1) per-splat buffers; re-ordered on each sort.
        self._vb_center = gloo.VertexBuffer(divisor=1)
        self._vb_cov_a = gloo.VertexBuffer(divisor=1)
        self._vb_cov_b = gloo.VertexBuffer(divisor=1)
        self._vb_color = gloo.VertexBuffer(divisor=1)
        self.shared_program['a_center'] = self._vb_center
        self.shared_program['a_cov_a'] = self._vb_cov_a
        self.shared_program['a_cov_b'] = self._vb_cov_b
        self.shared_program['a_color'] = self._vb_color

        self._draw_mode = 'triangle_strip'
        # Premultiplied "over", no depth test/write (we sort on the CPU).
        self.set_gl_state(
            depth_test=False, cull_face=False, blend=True,
            blend_func=('one', 'one_minus_src_alpha'),
        )

        self.set_data(positions, covariances, colors)

    @property
    def positions(self):
        """The (N, 3) array of Gaussian centers."""
        return self._gs_pos

    @property
    def covariances(self):
        """The (N, 3, 3) array of per-Gaussian 3D covariance matrices."""
        a, b = self._gs_cov_a, self._gs_cov_b
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
        return self._gs_rgba

    def set_data(self, positions=None, covariances=None, colors=None):
        """Update any subset of the per-Gaussian data arrays.

        Parameters not supplied are left unchanged. See the class docstring
        for the expected shapes.
        """
        if positions is not None:
            pos = np.ascontiguousarray(positions, dtype=np.float32)
            if pos.ndim != 2 or pos.shape[1] != 3:
                raise ValueError('positions must have shape (N, 3), got '
                                 f'{pos.shape}')
            self._gs_pos = pos
            lo, hi = pos.min(0), pos.max(0)
            self._probes = np.array([
                lo, hi, [lo[0], hi[1], lo[2]], [hi[0], lo[1], hi[2]],
            ], dtype=np.float32)
        if covariances is not None:
            cov = np.asarray(covariances, dtype=np.float32)
            if cov.ndim != 3 or cov.shape[1:] != (3, 3):
                raise ValueError('covariances must have shape (N, 3, 3), got '
                                 f'{cov.shape}')
            # Pack the symmetric 3x3 as cov_a=(S00,S01,S02), cov_b=(S11,S12,S22).
            self._gs_cov_a = np.ascontiguousarray(cov[:, 0, :])
            self._gs_cov_b = np.ascontiguousarray(
                np.stack([cov[:, 1, 1], cov[:, 1, 2], cov[:, 2, 2]], axis=-1))
        if colors is not None:
            rgba = np.ascontiguousarray(colors, dtype=np.float32)
            if rgba.ndim != 2 or rgba.shape[1] != 4:
                raise ValueError('colors must have shape (N, 4) RGBA, got '
                                 f'{rgba.shape}')
            self._gs_rgba = rgba

        # Force a re-sort/upload on the next draw.
        self._last_sig = None
        self.update()

    def _sort(self, view):
        """Re-sort back-to-front and re-upload instance buffers if the camera
        moved. Returns without work when the view transform is unchanged."""
        tr = view.get_transform('visual', 'framebuffer')
        sig = tr.map(self._probes).ravel()
        if self._last_sig is not None and np.allclose(sig, self._last_sig):
            return
        self._last_sig = sig

        fb = tr.map(self._gs_pos)
        depth = fb[:, 2] / fb[:, 3]
        order = np.argsort(depth)[::-1]  # draw back to front

        self._vb_center.set_data(np.ascontiguousarray(self._gs_pos[order]))
        self._vb_cov_a.set_data(np.ascontiguousarray(self._gs_cov_a[order]))
        self._vb_cov_b.set_data(np.ascontiguousarray(self._gs_cov_b[order]))
        self._vb_color.set_data(np.ascontiguousarray(self._gs_rgba[order]))

    def _prepare_draw(self, view):
        if self._gs_pos is None or len(self._gs_pos) == 0:
            return False
        self._sort(view)
        return True

    def _prepare_transforms(self, view):
        prog = view.view_program
        prog.vert['visual_to_framebuffer'] = \
            view.get_transform('visual', 'framebuffer')
        prog.vert['framebuffer_to_render'] = \
            view.get_transform('framebuffer', 'render')

    def _compute_bounds(self, axis, view):
        if self._gs_pos is None or len(self._gs_pos) == 0:
            return None
        return self._gs_pos[:, axis].min(), self._gs_pos[:, axis].max()
