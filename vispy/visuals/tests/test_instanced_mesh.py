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
        assert np.allclose(render[10, 10], (127, 0, 0, 255), atol=1)
        assert np.allclose(render[-10, -10], (0, 0, 255, 255))
        assert np.allclose(render[30, 40], (0, 0, 0, 255))


@requires_pyopengl()
@requires_application()
def test_compute_bounds():
    size = (80, 60)
    with TestingCanvas(size=size) as c:
        use(gl='gl+')
        vert = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        faces = np.array([[0, 1, 0]])
        pos = np.array([[0, 0, 0], [10, 20, 30]], dtype=np.float32)
        trans = np.array([np.eye(3), np.eye(3)], dtype=np.float32)

        mesh = scene.visuals.InstancedMesh(
            vertices=vert, faces=faces,
            instance_positions=pos,
            instance_transforms=trans,
        )
        v = c.central_widget.add_view(border_width=0)
        v.add(mesh)

        assert mesh._compute_bounds(0, None) == (0.0, 11.0)
        assert mesh._compute_bounds(1, None) == (0.0, 21.0)
        assert mesh._compute_bounds(2, None) == (0.0, 31.0)


@requires_pyopengl()
@requires_application()
def test_compute_bounds_with_rotation():
    size = (80, 60)
    with TestingCanvas(size=size) as c:
        use(gl='gl+')
        vert = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]])
        # 90-degree rotation around Z: x -> y, y -> -x
        rot90z = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float32)
        pos = np.array([[0, 0, 0], [5, 5, 0]], dtype=np.float32)
        trans = np.array([np.eye(3), rot90z], dtype=np.float32)

        mesh = scene.visuals.InstancedMesh(
            vertices=vert, faces=faces,
            instance_positions=pos,
            instance_transforms=trans,
        )
        v = c.central_widget.add_view(border_width=0)
        v.add(mesh)

        bx = mesh._compute_bounds(0, None)
        by = mesh._compute_bounds(1, None)
        bz = mesh._compute_bounds(2, None)

        # Instance 0 (identity): x=[0,1], y=[0,1], z=[0,0]
        # Instance 1 (rot90z at (5,5,0)):
        #   (0,0,0)->(5,5,0), (1,0,0)->(5,6,0), (0,1,0)->(4,5,0)
        assert bx == (0.0, 5.0)
        assert by == (0.0, 6.0)
        assert bz == (0.0, 0.0)


run_tests_if_main()
