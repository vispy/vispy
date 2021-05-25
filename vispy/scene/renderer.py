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

        from vispy.scene.visuals import Mesh
        visuals = [node for node in iter_tree(self.canvas.scene)
                   if isinstance(node, Mesh)]
        prog_visuals = []
        for visual in visuals:
            visual._prepare_draw(None)
            visual.set_gl_state(preset=None)

            vert_func = Function(vert_accumulate)
            frag_func = Function(frag_accumulate)
            prog_visuals.append(dict(vert=vert_func, frag=frag_func))

            visual_to_scene = visual.get_transform('visual', 'scene')
            vert_func['visual_to_scene'] = visual_to_scene
            vert_func['depth'] = Varying('depth', 'float')
            frag_func['depth'] = vert_func['depth']
            vert_func['position'] = visual.view_program.vert['position']

            hook_vert = visual._get_hook('vert', 'post')
            hook_frag = visual._get_hook('frag', 'post')
            # Hook this function in last position.
            # XXX: No guarantee that there is no hook with a higher position
            # index, but unlikely. (If needed, list all hook positions and
            # choose an higher index.)
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

    def resize(self, size):
        height_width = size[::-1]
        channels = self.color_buffer.shape[2:]
        self.color_buffer.resize(height_width + channels)
        self.depth_buffer.resize(height_width)
        # XXX: resize doesn't preserve channel dimensions if not passed (reset
        # to 1 channel). Bug or feature?
        channels = self.accumulation_buffer.shape[2:]
        self.accumulation_buffer.resize(height_width + channels)
        self.revealage_buffer.resize(height_width)

    def render(self, bgcolor=None):
        if bgcolor is None:
            bgcolor = (1, 1, 1, 1)
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
        # canvas.draw_visual(canvas.scene_with_transparent_only)
        canvas.draw_visual(canvas.scene)
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
        # canvas.draw_visual(canvas.scene_with_transparent_only)
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
        canvas.context.clear(color=bgcolor)
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
