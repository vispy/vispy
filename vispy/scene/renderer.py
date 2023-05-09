# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""A renderer supporting weighted blended order-independent transparency.

The computed transparency is approximate but emulates transparency well in most
cases.

One artefact that might arise is that a transparent object very close to the
camera might appear opaque and occlude the background. The solution is to
ensure some distance between the camera and the object.

Notes
-----
.. [1] McGuire, Morgan, and Louis Bavoil. "Weighted blended order-independent
   transparency." Journal of Computer Graphics Techniques 2.4 (2013).
"""

import numpy as np

from vispy import gloo
from vispy.visuals.shaders import Function, Varying


vert_accumulate = """
void compute_depth()
{
    vec3 a_position = $position;
    $depth = -$visual_to_scene(vec4(a_position, 1.0)).z;
}
"""

frag_accumulate = """
void accumulate()
{
    float v_depth = $depth;
    float abs_z = abs(v_depth);
    float alpha = gl_FragColor.a;

    float weight;

    // Variant 0: No depth weighting.
    //weight = 1.0;

    // Variants 1-4 are equations (7-10) in [1].

    // Variant 1
    // XXX: Does not give order-independent results on three parallel RGB
    // planes.
    //weight = 10.0 / (1e-5 + pow(abs_z / 5.0, 2.0) + pow(abs_z / 200.0, 6.0));
    //weight = alpha * clamp(weight, 1e-2, 3e3);

    // Variant 2
    //weight = 10.0 / (1e-5 + pow(abs_z / 10.0, 3.0) + pow(abs_z / 200.0, 6.0));
    //weight = alpha * clamp(weight, 1e-2, 3e3);

    // Variant 3
    //weight = 3e-2 / (1e-5 + pow(abs_z / 200.0, 4.0));
    //weight = alpha * clamp(weight, 1e-2, 3e3);

    // Variant 4
    weight = 3e3 * pow(1 - gl_FragCoord.z, 3.0);
    weight = alpha * max(weight, 1e-2);

    float u_pass = $u_pass;
    if(u_pass == 0.0) {
        gl_FragColor *= weight;
    } else if (u_pass == 1.0) {
        gl_FragColor = vec4(alpha);
    }
}
"""

vert_compose = """
attribute vec2 a_position;
varying vec2 v_texcoord;

void main(void)
{
    gl_Position = vec4(a_position, 0, 1);
    v_texcoord = (a_position + 1.0) / 2.0;
}
"""

frag_compose = """
uniform sampler2D tex_accumulation;
uniform sampler2D tex_revealage;

varying vec2 v_texcoord;

void main(void)
{
    vec4 accum = texture2D(tex_accumulation, v_texcoord);
    float r = texture2D(tex_revealage, v_texcoord).r;
    float a = clamp(accum.a, 1e-4, 5e4);
    gl_FragColor = vec4(accum.rgb / a, r);
}
"""

vert_copy = """
attribute vec2 a_position;
varying vec2 v_texcoord;

void main(void)
{
    gl_Position = vec4(a_position, 0, 1);
    v_texcoord = (a_position + 1.0) / 2.0;
}
"""

frag_copy = """
uniform sampler2D tex_color;

varying vec2 v_texcoord;

void main(void)
{
    gl_FragColor = texture2D(tex_color, v_texcoord);
}
"""


def _classify_nodes(scene):
    def is_drawable(node):
        return hasattr(node, 'draw')

    from vispy.visuals import MeshVisual

    def is_meshlike(node):
        return (
            isinstance(node, MeshVisual)
            # Compound visuals with a Mesh. Not sure they are defined
            # consistently.
            or hasattr(node, "mesh")
            or hasattr(node, "_mesh")
            # XXX: Check if there are other visuals to catch.
            # TODO: Standardise the structure of drawable (compound)
            #       visuals for consistent identification?
        )

    def get_sub_mesh_or_visual(visual):
        """Return the mesh visual of this visual.

        The mesh is either the visual itself or a subvisual, as for compound
        visuals like Box and Sphere.
        """
        # XXX: Assuming all mesh-based visuals are either a Mesh visual or a
        # compound visual with a `_mesh` attribute to a Mesh visual.
        # TODO: Verify this assumption.
        return visual._mesh if hasattr(visual, "_mesh") else visual

    # Classify the nodes of the scene graph into transparent/opaque,
    # drawable, and mesh-like, to:
    # - modify the shader programs of the transparent nodes,
    # - later draw the opaque and transparent subsets separately.
    # XXX: Restrict transparency to mesh-like visuals for now. Should be
    #      extended to lines...
    def iter_node_tree(node):
        yield node
        for child in node.children:
            yield from iter_node_tree(child)

    nodes = {
        node: dict(
            drawable=is_drawable(node),
            meshlike=is_meshlike(node),
            visual=node,
            mesh=get_sub_mesh_or_visual(node),
            transparent=None,   # Set in a second pass below.
        )
        for node in iter_node_tree(scene)
    }
    for node, properties in nodes.items():
        if not properties['meshlike']:
            continue
        mesh = properties['mesh']
        # XXX: This is a heuristic.
        # TODO: Define more formally how to distinguish opaque from
        # transparent visuals.
        properties['transparent'] = mesh.color.alpha < 1

    return nodes


def _extend_programs(node_properties):
    """Add the glsl program for transparency at the end of the programs of the
    transparent visuals.
    """
    programs = []
    for node, properties in node_properties.items():
        if not (properties['meshlike'] and properties['transparent']):
            continue
        visual = properties['visual']
        mesh = properties['mesh']

        # XXX: Without this the `view_program.vert['position']` is not
        # defined.
        mesh._prepare_draw(None)
        # The default state of visuals is not compatible with the state for
        # transparent rendering.
        # XXX: Save the state and restore later instead? Or overide the
        # state locally when redering?
        mesh.set_gl_state(preset=None)

        vert_func = Function(vert_accumulate)
        frag_func = Function(frag_accumulate)
        programs.append(dict(vert=vert_func, frag=frag_func))

        visual_to_scene = visual.get_transform('visual', 'scene')
        vert_func['visual_to_scene'] = visual_to_scene
        vert_func['depth'] = Varying('depth', 'float')
        frag_func['depth'] = vert_func['depth']
        vert_func['position'] = mesh.view_program.vert['position']

        hook_vert = mesh._get_hook('vert', 'post')
        hook_frag = mesh._get_hook('frag', 'post')
        # Add in last position.
        # XXX: No guarantee that there is no hook with a higher position
        # index, but unlikely. (If needed, list all hook positions and
        # choose a higher index.)
        position = 1000
        hook_vert.add(vert_func(), position=position)
        hook_frag.add(frag_func(), position=position)

    return programs


class WeightedTransparencyRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

        # TODO: Observe when a new scene is set in the canvas, and update the
        # callback.
        canvas.scene.events.children_change.connect(self.on_scene_changed)

        width, height = canvas.size
        self.color_buffer = gloo.Texture2D((height, width, 4), format='rgba')
        self.depth_buffer = gloo.RenderBuffer((height, width), 'depth')
        # An RGBA32F float texture for accumulating the weighted colors.
        # Note: The 32bit float precision seems important to avoid artefacts.
        self.accumulation_buffer = gloo.Texture2D(
            (height, width, 4),
            format='rgba',
            internalformat='rgba32f',
        )
        # A single-channel float texture (R32F) for the revealage.
        # The revelage is the amount of background revealed per fragment, as
        # opposed to coverage used in related blended order-independent
        # transparency methods.
        self.revealage_buffer = gloo.Texture2D(
            (height, width),
            format='red',
            internalformat='r32f',
        )

        self.framebuffer = gloo.FrameBuffer(depth=self.depth_buffer)

        # Post composition.
        # A quad (two triangles) spanning the framebuffer area.
        quad_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
        indices = gloo.IndexBuffer(indices)
        self.indices = indices
        prog_composite = gloo.Program(vert_compose, frag_compose)
        prog_composite['tex_accumulation'] = self.accumulation_buffer
        prog_composite['tex_revealage'] = self.revealage_buffer
        prog_composite['a_position'] = quad_corners
        self.prog_composite = prog_composite

        # Copy the rendered scene onto the default frame buffer.
        # TODO: Use blitting?
        prog_copy = gloo.Program(vert_copy, frag_copy)
        prog_copy['tex_color'] = self.color_buffer
        prog_copy['a_position'] = quad_corners
        self.prog_copy = prog_copy

        self._scene_changed = True
        self._draw_order = {}

    def on_scene_changed(self, event):
        self._scene_changed = True

    def resize(self, size):
        height_width = size[::-1]
        channels = self.color_buffer.shape[2:]
        self.color_buffer.resize(height_width + channels)
        self.depth_buffer.resize(height_width)
        channels = self.accumulation_buffer.shape[2:]
        self.accumulation_buffer.resize(height_width + channels)
        self.revealage_buffer.resize(height_width)

    def draw_visual(self, visual, subset=None):
        """Draw a visual and its children to the currently active framebuffer.

        Parameters
        ----------
        visual : Visual
            The root visual.
        subset : {None, 'opaque', 'transparent'}, optional
            Select the subset of visuals to draw: 'opaque' only, 'transparent'
            only, or all (None).
        """
        assert subset in (None, 'opaque', 'transparent')

        canvas = self.canvas

        # prof = self.Profiler()

        # make sure this canvas's context is active
        canvas.set_current()

        try:
            canvas._drawing = True

            if self._scene_changed:
                self.nodes = _classify_nodes(self.canvas.scene)
                # XXX(asnt): Check if we need to delete the old program hooks
                # before adding the new ones or if they get deleted
                # automatically.
                self.prog_visuals = _extend_programs(self.nodes)
                self._draw_order = {}
                self._scene_changed = False

            if subset is None:
                in_subset = {node: True for node in self.nodes}
            elif subset == 'opaque':
                in_subset = {
                    node: prop['drawable'] and not prop['transparent']
                    for node, prop in self.nodes.items()
                }
            elif subset == 'transparent':
                in_subset = {
                    node: prop['drawable'] and prop['transparent']
                    for node, prop in self.nodes.items()
                }

            # get order to draw visuals
            if visual not in self._draw_order:
                self._draw_order[visual] = canvas._generate_draw_order(visual)
            order = self._draw_order[visual]

            # Draw and
            # - avoid branches with visible=False,
            # - skip visuals not in the selected subset (opaque or
            #   transparent).
            stack = []
            invisible_node = None
            for node, start in order:
                if start:
                    stack.append(node)
                    if invisible_node is None:
                        if not node.visible:
                            # disable drawing until we exit this node's subtree
                            invisible_node = node
                        else:
                            if not in_subset[node]:
                                continue
                            if hasattr(node, 'draw'):
                                node.draw()
                                # prof.mark(str(node))
                else:
                    if node is invisible_node:
                        invisible_node = None
                    stack.pop()
        finally:
            canvas._drawing = False

    def render(self, bgcolor):
        canvas = self.canvas

        offset = 0, 0
        canvas_size = self.canvas.size

        def push_fbo():
            canvas.push_fbo(self.framebuffer, offset, canvas_size)

        def pop_fbo():
            canvas.pop_fbo()

        # 1. Draw opaque objects.

        canvas.context.set_state(
            cull_face=True,
            depth_test=True,
            blend=False,
            depth_mask=True,
        )
        self.framebuffer.color_buffer = self.color_buffer
        push_fbo()
        canvas.context.clear(color=bgcolor, depth=True)
        self.draw_visual(canvas.scene, subset='opaque')
        pop_fbo()

        # 2. Draw transparent objects.

        canvas.context.set_state(
            preset=None,
            cull_face=False,
            blend=True,
            depth_test=True,   # Read the depth for opaque objects.
            depth_mask=False,  # Do not overwrite the depth.
        )

        # TODO: Merge the two render passes into a single render pass with two
        # render targets.
        # TODO: Add support for multiple render targets to gloo.

        # 2.1 Accumulate contributions from all objects.

        pass_ = 0
        for prog in self.prog_visuals:
            prog['frag']['u_pass'] = float(pass_)
        self.framebuffer.color_buffer = self.accumulation_buffer
        push_fbo()
        canvas.context.clear(
            color=(0, 0, 0, 0),
            depth=False,
            stencil=False,
        )
        canvas.context.set_blend_equation('func_add')
        canvas.context.set_blend_func('one', 'one')
        self.draw_visual(canvas.scene, subset='transparent')
        pop_fbo()

        pass_ = 1
        for prog in self.prog_visuals:
            prog['frag']['u_pass'] = float(pass_)
        self.framebuffer.color_buffer = self.revealage_buffer
        push_fbo()
        canvas.context.clear(
            color=(1, 1, 1, 1),
            depth=False,
            stencil=False,
        )
        canvas.context.set_blend_func('zero', 'one_minus_src_alpha')
        self.draw_visual(canvas.scene, subset='transparent')
        canvas.draw_visual(canvas.scene)
        pop_fbo()

        # 2.2 Do the compositing of the accumulation of the transparent with
        # the opaque.

        canvas.context.set_state(
            depth_test=False,
            blend=True,
            depth_mask=False,
        )
        self.framebuffer.color_buffer = self.color_buffer
        push_fbo()
        canvas.context.set_blend_func('one_minus_src_alpha', 'src_alpha')
        self.prog_composite.draw('triangles', self.indices)
        pop_fbo()

        # 3. Copy result to default frame buffer.
        # TODO: Use glBlitFramebuffer instead. Should be faster?
        canvas.context.set_state(
            depth_test=False,
            blend=False,
            depth_mask=False,
        )
        canvas.context.clear(color=bgcolor)
        self.prog_copy.draw('triangles', self.indices)
