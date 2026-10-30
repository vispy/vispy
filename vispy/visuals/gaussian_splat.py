# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""A visual for rendering 3D Gaussian Splatting scenes."""

import numpy as np

from .. import gloo
from ..color import ColorArray
from ..util import logger
from .visual import Visual

# per-splat records (16 floats = 4 RGBA32F texels) are stored in a data texture
# and fetched in the vertex shader; only the sorted draw order is re-uploaded
# per frame
# rows hold whole splats, so splat n sits at (n // _SPLATS_PER_ROW,
# n % _SPLATS_PER_ROW) and its 4 texels are a span within that one row
# the order is uploaded as that (column, row) slot rather than as a running
# index, because a single float32 index would only stay exact to 2**24 and
# would cap the visual well below what the texture can hold
_SPLATS_PER_ROW = 4096
_TEXELS_PER_SPLAT = 4
_TEX_WIDTH = _SPLATS_PER_ROW * _TEXELS_PER_SPLAT   # 16384, the common GL max
_MAX_TEX_HEIGHT = 16384
_MAX_SPLATS = _SPLATS_PER_ROW * _MAX_TEX_HEIGHT


def _parse_positions(positions):
    pos = np.ascontiguousarray(positions, dtype=np.float32)
    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"positions must have shape (N, 3), got {pos.shape}")
    return pos


def _parse_covariances(covariances):
    """Split symmetric 3x3s into (S00, S01, S02) and (S11, S12, S22)."""
    cov = np.asarray(covariances, dtype=np.float32)
    if cov.ndim != 3 or cov.shape[1:] != (3, 3):
        raise ValueError(
            f"covariances must have shape (N, 3, 3), got {cov.shape}"
        )
    return np.ascontiguousarray(cov[:, 0, :]), np.ascontiguousarray(
        np.stack([cov[:, 1, 1], cov[:, 1, 2], cov[:, 2, 2]], axis=-1)
    )


def _check_unit_range(arr, name):
    """Raise unless every value is in [0, 1], as ColorArray requires."""
    if arr.size and (arr.min() < 0 or arr.max() > 1):
        raise ValueError(f"{name} values must be between 0 and 1")


def _parse_colors(colors, count):
    """Validate `colors` and return (RGB, alpha or None).

    ``count`` is used only to broadcast a single color over every splat.
    """
    if isinstance(colors, str) or np.ndim(colors) <= 1:
        # one color for all splats, e.g. 'white', '#ff000080' or (1, 0, 0)
        colors = np.broadcast_to(ColorArray(colors).rgba, (count, 4))
    arr = np.asarray(colors, dtype=np.float32)
    if arr.ndim == 2 and arr.shape[1] in (3, 4):
        _check_unit_range(arr, "colors")
        rgb = np.ascontiguousarray(arr[:, :3])
        alpha = np.ascontiguousarray(arr[:, 3]) if arr.shape[1] == 4 else None
        return rgb, alpha
    raise ValueError(
        "colors must be a single color, or have shape (N, 3) RGB or (N, 4) "
        f"RGBA; got shape {arr.shape}"
    )


def _parse_opacities(opacities, count):
    arr = np.asarray(opacities, dtype=np.float32)
    if arr.ndim == 0:
        arr = np.broadcast_to(arr, (count,))
    elif arr.ndim != 1:
        raise ValueError(
            f"opacities must be a scalar or have shape (N,), got {arr.shape}"
        )
    _check_unit_range(arr, "opacities")
    return np.ascontiguousarray(arr)


def _check_lengths(pos, cov_a, rgb, alpha):
    counts = {"covariances": len(cov_a), "colors": len(rgb),
              "opacities": len(alpha)}
    bad = [f"{k} has length {v}" for k, v in counts.items() if v != len(pos)]
    if bad:
        raise ValueError(
            f"positions has length {len(pos)}, but " + ", ".join(bad)
        )


VERTEX_SHADER = """
attribute vec2 a_quad;      // per-vertex: quad corner in [-1, 1]
attribute vec2 a_slot;      // per-instance: (column, row) of the splat to draw

uniform sampler2D u_splats; // static per-splat data (RGBA32F)
uniform vec2 u_tex_size;    // data texture size in texels (width, height)

uniform float u_eps;        // finite-difference step (visual units)
uniform float u_antialias;  // 1.0 to compensate opacity for the dilation

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
    // the slot arrives already split into (column, row), so there is no
    // per-vertex division and no index too large to hold exactly in a float
    float row = a_slot.y;
    float col0 = a_slot.x * 4.0;   // _TEXELS_PER_SPLAT
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
    float ca0 = dot(r0, sr0);               // Sigma2_00 before dilation
    float cb = dot(r0, sr1);                // Sigma2_01
    float cc0 = dot(r1, sr1);               // Sigma2_11 before dilation
    float ca = ca0 + c_dilation;
    float cc = cc0 + c_dilation;

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
    if (u_antialias > 0.5) {
        // scenes trained with anti-aliasing (Mip-Splatting style) expect the
        // dilation to conserve each splat's total weight, so scale the peak
        // opacity by the ratio of the areas before and after dilating
        float det0 = max(ca0 * cc0 - cb * cb, 0.0);
        v_color.a *= sqrt(det0 / det);
    }

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
    colors : array or Color
        One of:

        * a single color for every splat -- anything ``Color`` accepts, such
          as ``'white'``, ``'#ff000080'`` or ``(1, 0, 0)``;
        * a per-splat color, as (N, 3) RGB or (N, 4) RGBA in [0, 1].
    opacities : (N,) array or float, optional
        Per-Gaussian peak opacity in [0, 1]. Required unless ``colors`` is
        given as (N, 4) RGBA, which supplies it as the alpha channel. A single
        color also carries an alpha (opaque unless the color says otherwise),
        which ``opacities`` overrides. Named in the plural because the scene
        graph's ``Node.opacity`` is a separate, whole-visual alpha.
    antialias : bool
        Compensate opacity for the screen-space low-pass dilation, as expected
        by scenes trained with anti-aliasing (e.g. Mip-Splatting or gsplat's
        ``"antialiased"`` mode). Leave off (the default) for scenes trained
        like the original 3DGS, which would otherwise render too faint. See
        the ``antialias`` property.

    Notes
    -----
    Per-splat records are stored once in a data texture and fetched in the
    vertex shader by texture slot. The splats are depth-sorted on the CPU, but
    only the (N, 2) draw order is re-uploaded, and only when the view
    *direction* rotates (pan, zoom and static redraws reuse the existing
    order) -- so the heavy per-splat data never moves after upload, which
    keeps interaction smooth for up to a few million splats.

    Color is a fixed per-Gaussian RGBA value; view-dependent color is often
    included in splat data, but yet not supported here.
    """

    def __init__(self, positions, covariances, colors, opacities=None, *,
                 antialias=False):
        Visual.__init__(self, VERTEX_SHADER, FRAGMENT_SHADER)

        self._splat_pos = None
        self._splat_cov_a = None
        self._splat_cov_b = None
        self._splat_rgb = None      # (N, 3) color
        self._splat_alpha = None    # (N,) peak opacity

        # cached bounding box, rows (min, max), for _compute_bounds
        self._bounds = None

        # view direction (normalized framebuffer-depth gradient) at the last
        # sort; the order only changes when this rotates, so _sort skips pan,
        # zoom and static redraws (see _sort).
        self._last_view_dir = None

        # the real GL_MAX_TEXTURE_SIZE is only readable once a context exists
        self._checked_texture_size = False

        # instancing quad, drawn as a triangle strip
        quad = np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype=np.float32)
        self.shared_program["a_quad"] = gloo.VertexBuffer(quad)

        # per-instance draw order, far -> near, as (column, row) texture
        # slots; reuploaded on _sort
        self._slot_vbo = gloo.VertexBuffer(
            np.zeros((1, 2), np.float32), divisor=1)
        self.shared_program["a_slot"] = self._slot_vbo

        # static per-splat data texture
        self._tex = gloo.Texture2D(
            np.zeros((1, _TEX_WIDTH, 4), np.float32),
            interpolation="nearest",
            internalformat="rgba32f",
        )
        self.shared_program["u_splats"] = self._tex
        self.shared_program["u_tex_size"] = (float(_TEX_WIDTH), 1.0)

        self._draw_mode = "triangle_strip"

        # premultiplied "over" blending, sort back-to-front on the CPU (_sort)
        self.set_gl_state(
            depth_test=False,
            cull_face=False,
            blend=True,
            blend_func=("one", "one_minus_src_alpha"),
        )

        self.antialias = antialias
        self.set_data(positions, covariances, colors, opacities)

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
        return np.concatenate(
            [self._splat_rgb, self._splat_alpha[:, None]], axis=-1
        )

    @property
    def opacities(self):
        """The (N,) array of per-Gaussian peak opacities.

        Not ``opacity``: the scene graph's ``Node.opacity`` is a separate,
        whole-visual alpha and would shadow this name on
        ``scene.visuals.GaussianSplat``.
        """
        return self._splat_alpha

    @property
    def antialias(self):
        """Whether opacity is compensated for the low-pass dilation.

        Every splat's screen-space covariance is dilated by a small fixed
        amount so that sub-pixel splats don't alias. Scenes trained with
        anti-aliasing expect that dilation to leave each splat's total weight
        unchanged, i.e. its peak opacity scaled down by
        ``sqrt(det(cov2d) / det(cov2d + dilation))``; scenes trained like the
        original 3DGS expect the opacity as stored. The training mode is not
        part of the standard ply layout, though some tools record it (Postshot
        writes a ``postshot.anti_aliasing=1`` header comment).
        """
        return self._antialias

    @antialias.setter
    def antialias(self, value):
        self._antialias = bool(value)
        self.shared_program["u_antialias"] = float(self._antialias)
        self.update()

    def set_data(self, positions=None, covariances=None, colors=None,
                 opacities=None):
        """Update any subset of the per-Gaussian data arrays.

        Parameters not supplied are left unchanged. See the class docstring
        for the expected shapes. Everything is validated before any of it is
        committed, so a call that raises leaves the visual as it was.
        """
        if (opacities is not None and colors is not None
                and np.ndim(colors) == 2 and np.shape(colors)[-1] == 4):
            raise ValueError(
                "opacities is already given by the alpha channel of "
                "(N, 4) RGBA colors; pass (N, 3) RGB to set it separately"
            )

        # unsupplied fields fall back to what is already held
        pos = self._splat_pos if positions is None else _parse_positions(positions)
        cov_a, cov_b = ((self._splat_cov_a, self._splat_cov_b)
                        if covariances is None else _parse_covariances(covariances))
        rgb, alpha = self._splat_rgb, self._splat_alpha
        if colors is not None:
            rgb, rgba_alpha = _parse_colors(colors, len(pos))
            alpha = alpha if rgba_alpha is None else rgba_alpha

        if alpha is None and opacities is None:
            raise ValueError(
                "opacities is required unless colors is a single color or "
                "(N, 4) RGBA; pass it alongside (N, 3) RGB colors"
            )
        if opacities is not None:
            alpha = _parse_opacities(opacities, len(pos))
        _check_lengths(pos, cov_a, rgb, alpha)

        # build the texture before committing: _pack_texture can still raise on
        # a capacity overflow, and a half-applied update would leave the shader
        # pointing at records that were never uploaded
        tex = self._pack_texture(pos, cov_a, cov_b, rgb, alpha)

        # ---- past here nothing can fail ----
        self._splat_pos, self._splat_cov_a, self._splat_cov_b = pos, cov_a, cov_b
        self._splat_rgb, self._splat_alpha = rgb, alpha

        if positions is not None:
            if len(pos):
                lo, hi = pos.min(0), pos.max(0)
                self._bounds = np.array([lo, hi], dtype=np.float32)
                # finite-difference step: ~1% of the largest bounding-box side,
                # so it stays well-conditioned whatever the data's units
                extent = float((hi - lo).max())
                self.shared_program["u_eps"] = (
                    1e-2 * extent if extent > 0 else 1e-2
                )
            else:
                # an empty visual draws nothing (_prepare_draw) and has no
                # bounds to contribute to a camera's set_range()
                self._bounds = None

        self._tex.set_data(tex)
        self.shared_program["u_tex_size"] = (
            float(tex.shape[1]), float(tex.shape[0])
        )
        # force a re-sort (which re-uploads the draw order) on the next draw
        self._last_view_dir = None
        self.update()

    @staticmethod
    def _pack_texture(pos, cov_a, cov_b, rgb, alpha):
        """Build the per-splat data texture (uploaded once per data change;
        the sort only re-uploads the draw order)."""
        m = len(pos)
        if m > _MAX_SPLATS:
            raise ValueError(
                f"{m:,} splats exceed what this visual can address: the limit "
                f"is {_MAX_SPLATS:,} ({_SPLATS_PER_ROW} splats per row x "
                f"{_MAX_TEX_HEIGHT} rows of the data texture)"
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
        packed[:, 2, 1:4] = rgb                       # rgb
        packed[:, 3, 0] = alpha                       # a

        height = int(np.ceil(m / _SPLATS_PER_ROW)) if m else 1
        tex = np.zeros((height, _TEX_WIDTH, 4), np.float32)
        tex.reshape(-1, 4)[: m * _TEXELS_PER_SPLAT] = packed.reshape(-1, 4)
        return tex

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
            # a transform that drops z leaves no depth to sort by, but the
            # index buffer still has to name every splat or only the ones it
            # happens to hold get drawn
            if self._last_view_dir is not None:
                return
            self._upload_order(np.arange(len(self._splat_pos)))
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
            order = np.argsort(key, kind="stable")
        else:
            # all splats share a depth plane: any order composites the same
            order = np.arange(len(depth))

        self._upload_order(order)

    def _upload_order(self, order):
        """Upload a draw order as (column, row) texture slots.

        Both components stay small enough to be exact in float32 however many
        splats there are, which a running index would not.
        """
        slots = np.empty((len(order), 2), np.float32)
        slots[:, 0] = order % _SPLATS_PER_ROW     # column, in splats
        slots[:, 1] = order // _SPLATS_PER_ROW    # row
        self._slot_vbo.set_data(slots)

    def _check_texture_size(self, view):
        """Warn once if the data texture exceeds this context's real limit.

        _MAX_TEX_HEIGHT is a conservative guess made before a GL context
        exists; the actual GL_MAX_TEXTURE_SIZE is only knowable at draw time,
        and a texture over it fails to allocate with no useful message.
        """
        self._checked_texture_size = True
        canvas = getattr(view.transforms, "canvas", None)
        context = getattr(canvas, "context", None)
        if context is None:
            return
        limit = context.capabilities.get("max_texture_size")
        height = self._tex.shape[0]
        if limit and max(height, _TEX_WIDTH) > limit:
            logger.warning(
                "GaussianSplatVisual needs a %d x %d data texture but this "
                "context supports at most %d in either dimension; the splats "
                "will not render. Use fewer splats.",
                _TEX_WIDTH, height, limit,
            )

    def _prepare_draw(self, view):
        if self._splat_pos is None or len(self._splat_pos) == 0:
            return False
        if not self._checked_texture_size:
            self._check_texture_size(view)
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
