import numpy as np
from vispy import scene, use

from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl)


def setup_module(module):
    use(gl='gl+')


def teardown_module(module):
    use(gl='gl2')


@requires_pyopengl()
@requires_application()
def test_mesh_with_vertex_values():
    size = (80, 60)
    with TestingCanvas(size=size) as c:
        use(gl='gl+')
        vert = np.array([[0, 0, 0], [0, 30, 0], [40, 0, 0]])
        faces = np.array([0, 1, 2])
        pos = np.array([[0, 0, 0], [80, 60, 0]])
        # identity and rotate 180
        trans = np.array([
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ],
            [
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, 1],
            ],
        ])
        colors = ['red', 'blue']
        mesh = scene.visuals.InstancedMesh(
            vertices=vert, faces=faces, instance_positions=pos, instance_transforms=trans, instance_colors=colors
        )
        v = c.central_widget.add_view(border_width=0)
        v.add(mesh)
        render = c.render()
        assert np.allclose(render[10, 10], (255, 0, 0, 255))
        assert np.allclose(render[-10, -10], (0, 0, 255, 255))
        assert np.allclose(render[30, 40], (0, 0, 0, 255))


run_tests_if_main()
