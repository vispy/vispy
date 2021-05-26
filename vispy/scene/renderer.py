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
    float z = abs(v_depth);
    float alpha = gl_FragColor.a;

    float weight;
    weight = 3e-2 / (1e-5 + pow(z / 200.0, 4.0));
    weight = alpha * clamp(weight, 1e-2, 3e-3);
    //weight = 3e3 * (1 - pow(gl_FragCoord.z, 3.0));
    //weight = alpha * max(1e-2, weight);
    // XXX: Fix this weight.
    //weight = 1.0;

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
    // XXX: Fix the weight. See accumulation shader.
    //a = 1.0;
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


class WeightedTransparencyRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

        width, height = canvas.size
        # XXX: Not sure if buffer formats need to be specified explicitly
        # and/or matched to the format of the default frame buffer.
        self.color_buffer = gloo.Texture2D((height, width, 4), format='rgba')
        self.depth_buffer = gloo.RenderBuffer((height, width), 'depth')
        # An RGBA32F float texture for accumulating the weighted colors.
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

        def iter_tree(node):
            yield node
            for child in node.children:
                yield from iter_tree(child)

        import vispy
        from vispy.scene.visuals import Mesh

        def is_drawable(node):
            return hasattr(node, 'draw')

        def is_meshlike(node):
            return (
                isinstance(node, Mesh)
                # Compound visuals with a Mesh. Not sure they are defined
                # consistently.
                or hasattr(node, "mesh")
                or hasattr(node, "_mesh")
                # XXX: Check if there are other visuals to catch.
                # TODO: Standardise the structure of drawable (compound)
                #       visuals for consistent identification?
            )

        def get_sub_mesh_or_visual(visual):
            return (
                visual._mesh
                if isinstance(visual, vispy.visuals.CompoundVisual)
                else visual
            )

        # Classify the nodes of the scene graph into transparent/opaque,
        # drawable, and mesh-like, to:
        # - modify the shader programs of the transparent nodes,
        # - later draw the opaque and transparent subsets separately.
        # XXX: Restrict transparency to mesh-like visuals for now. Should be
        #      extended to lines...
        nodes = {
            node: dict(
                drawable=is_drawable(node),
                meshlike=is_meshlike(node),
                visual=node,
                mesh=get_sub_mesh_or_visual(node),
                transparent=None,   # Set in a second pass below.
            )
            for node in iter_tree(self.canvas.scene)
        }
        for node, properties in nodes.items():
            if not properties['meshlike']:
                continue
            mesh = properties['mesh']
            # XXX: This is a heuristic.
            # TODO: Define more formally how to distinguish opaque from
            #       transparent visuals.
            properties['transparent'] = mesh.color.alpha < 1

        self.nodes = nodes

        # Add the glsl program for transparency at the end of the programs of
        # the transparent visuals.
        prog_visuals = []
        for node, properties in nodes.items():
            if not (properties['meshlike'] and properties['transparent']):
                continue
            visual = properties['visual']
            mesh = properties['mesh']

            mesh._prepare_draw(None)
            mesh.set_gl_state(preset=None)

            vert_func = Function(vert_accumulate)
            frag_func = Function(frag_accumulate)
            prog_visuals.append(dict(vert=vert_func, frag=frag_func))

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

        self.prog_visuals = prog_visuals

        # Post composition.
        # A quad (two triangles) spanning the framebuffer area.
        quad_corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
        indices = gloo.IndexBuffer(indices)
        self.indices = indices
        prog_compose = gloo.Program(vert_compose, frag_compose)
        prog_compose['tex_accumulation'] = self.accumulation_buffer
        prog_compose['tex_revealage'] = self.revealage_buffer
        prog_compose['a_position'] = quad_corners
        self.prog_compose = prog_compose

        # Copy the rendered scene onto the default frame buffer.
        prog_copy = gloo.Program(vert_copy, frag_copy)
        prog_copy['tex_color'] = self.color_buffer
        prog_copy['a_position'] = quad_corners
        self.prog_copy = prog_copy

        self._draw_order = {}

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

        try:
            canvas._drawing = True
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
        # # TODO: Identify and draw opaque objects only.
        # # canvas.draw_visual(canvas.scene_with_opaque_only)
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

        # TODO: Add support for multiple render targets to gloo.
        # TODO: Merge the two render passes into a single render pass with two
        # render targets.

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
        # TODO: Only draw transparent objects.
        self.draw_visual(canvas.scene, subset='transparent')
        # canvas.draw_visual(canvas.scene)
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
        # TODO: Only draw transparent objects.
        self.draw_visual(canvas.scene, subset='transparent')
        canvas.draw_visual(canvas.scene)
        pop_fbo()

        # 2.2 Composite accumulations.

        # XXX: Check the settings for when rendering with opaque objects.
        canvas.context.set_state(
            preset=None,
            depth_test=False,
            blend=True,
            depth_mask=False,
        )
        # DEBUG: Render directly to the default frame buffer.
        # canvas.context.clear(color=bgcolor)
        # canvas.context.set_blend_func('one_minus_src_alpha', 'src_alpha')
        # self.prog_compose.draw('triangles', self.indices)
        # GOAL: Render to frame buffer object.
        self.framebuffer.color_buffer = self.color_buffer
        push_fbo()
        canvas.context.set_blend_func('one_minus_src_alpha', 'src_alpha')
        self.prog_compose.draw('triangles', self.indices)
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
