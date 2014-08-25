import numpy as np

from .... import gloo
from ....color import ColorArray
from ...shaders import ModularProgram
from ..visual import Visual

from .dash_atlas import DashAtlas
from .vertex import VERTEX_SHADER
from .fragment import FRAGMENT_SHADER

join = {'miter': 0, 'round': 1, 'bevel': 2}

caps = {'': 0, 'none': 0, '.': 0,
        'round': 1, ')': 1, '(': 1, 'o': 1,
        'triangle in': 2, '<': 2,
        'triangle out': 3, '>': 3,
        'square': 4, '=': 4, 'butt': 4,
        '|': 5}


def _bake(vtype, vertices, color, closed=False):
    """
    Bake a list of 2D vertices for rendering them as thick line. Each line
    segment must have its own vertices because of antialias (this means no
    vertex sharing between two adjacent line segments).
    """

    n = len(vertices)
    P = np.array(vertices).reshape(n, 2).astype(float)
    idx = np.arange(n)  # used to eventually tile the color array

    dx, dy = P[0] - P[-1]
    d = np.sqrt(dx*dx+dy*dy)

    # If closed, make sure first vertex = last vertex (+/- epsilon=1e-10)
    if closed and d > 1e-10:
        P = np.append(P, P[0]).reshape(n+1, 2)
        idx = np.append(idx, idx[-1])
        n += 1

    V = np.zeros(len(P), dtype=vtype)
    V['a_position'] = P

    # Tangents & norms
    T = P[1:] - P[:-1]

    N = np.sqrt(T[:, 0]**2 + T[:, 1]**2)
    # T /= N.reshape(len(T),1)
    V['a_tangents'][+1:, :2] = T
    V['a_tangents'][0, :2] = T[-1] if closed else T[0]
    V['a_tangents'][:-1, 2:] = T
    V['a_tangents'][-1, 2:] = T[0] if closed else T[-1]

    # Angles
    T1 = V['a_tangents'][:, :2]
    T2 = V['a_tangents'][:, 2:]
    A = np.arctan2(T1[:, 0]*T2[:, 1]-T1[:, 1]*T2[:, 0],
                   T1[:, 0]*T2[:, 0]+T1[:, 1]*T2[:, 1])
    V['a_angles'][:-1, 0] = A[:-1]
    V['a_angles'][:-1, 1] = A[+1:]

    # Segment
    L = np.cumsum(N)
    V['a_segment'][+1:, 0] = L
    V['a_segment'][:-1, 1] = L
    #V['a_lengths'][:,2] = L[-1]

    # Step 1: A -- B -- C  =>  A -- B, B' -- C
    V = np.repeat(V, 2, axis=0)[1:-1]
    V['a_segment'][1:] = V['a_segment'][:-1]
    V['a_angles'][1:] = V['a_angles'][:-1]
    V['a_texcoord'][0::2] = -1
    V['a_texcoord'][1::2] = +1
    idx = np.repeat(idx, 2)[1:-1]

    # Step 2: A -- B, B' -- C  -> A0/A1 -- B0/B1, B'0/B'1 -- C0/C1
    V = np.repeat(V, 2, axis=0)
    V['a_texcoord'][0::2, 1] = -1
    V['a_texcoord'][1::2, 1] = +1
    idx = np.repeat(idx, 2)

    I = np.resize(np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32), (n-1)*(2*3))
    I += np.repeat(4*np.arange(n-1, dtype=np.uint32), 6)

    # Length
    V['alength'] = L[-1] * np.ones(len(V))

    # Color
    color = ColorArray(color)
    if len(color) == 1:
        color = np.tile(color.rgba[0], (len(V), 1))
    elif len(color) == n:
        color = color.rgba[idx]
    else:
        raise ValueError('Color length %s does not match number of vertices '
                         '%s' % (len(color), n))
    V['color'] = color

    return gloo.VertexBuffer(V), gloo.IndexBuffer(I)


vtype = np.dtype([('a_position', 'f4', 2),
                  ('a_tangents', 'f4', 4),
                  ('a_segment',  'f4', 2),
                  ('a_angles',   'f4', 2),
                  ('a_texcoord', 'f4', 2),
                  ('alength', 'f4', 1),
                  ('color', 'f4', 4)])


class LineAgg(Visual):
    VERTEX_SHADER = VERTEX_SHADER
    FRAGMENT_SHADER = FRAGMENT_SHADER

    def __init__(self, path, dash_pattern='solid', color='black', width=2,
                 linecaps=('round', 'round'), dash_caps=('round', 'round'),
                 line_join='round', antialias=True, **kwargs):
        super(LineAgg, self).__init__(**kwargs)
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.da = DashAtlas()
        dash_index, dash_period = self.da[dash_pattern]

        self._V, self._I = _bake(vtype, path, color)

        self._U = dict(
            dash_index=dash_index,
            dash_period=dash_period,
            linejoin=join.get(line_join, 'round'),
            linecaps=(caps.get(linecaps[0], 'round'),
                      caps.get(linecaps[1], 'round')),
            dash_caps=(caps.get(dash_caps[0], 'round'),
                       caps.get(dash_caps[1], 'round')),
            linewidth=width,
            antialias=antialias)
        self._dash_atlas = gloo.Texture2D(self.da._data)

    def draw(self, event):
        gloo.set_state('translucent', depth_test=False)

        # check for transform changes
        data_doc = event.doc_transform()
        doc_px = event.entity_transform(map_from=event.document,
                                        map_to=event.framebuffer)
        px_ndc = event.entity_transform(map_from=event.framebuffer,
                                        map_to=event.ndc)
        vert = self._program.vert
        vert['doc_px_transform'] = doc_px.shader_map()
        vert['px_ndc_transform'] = px_ndc.shader_map()
        vert['transform'] = data_doc.shader_map()

        # attributes / uniforms are not available until program is built
        self._program.prepare()

        self._program.bind(self._V)
        uniforms = dict(
            closed=False,
            # color=(0.,0.,0.,1),
            linewidth=10.,
            antialias=1.0,
            miter_limit=4.0,
            #u_scale=(300, 300),
            dash_phase=0.0,
            # length=length,
            )
        for n, v in uniforms.iteritems():
            self._program[n] = v

        # WARNING/TODO: put the different sets of uniforms and put them in
        # attributes instead
        for n, v in self._U.iteritems():
            self._program[n] = v

        self._program['u_dash_atlas'] = self._dash_atlas
        self._program.draw('triangles', self._I)
