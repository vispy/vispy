import sys

from vispy import scene
from vispy.scene import XYZAxis


def main():
    canvas = scene.SceneCanvas(show=True)
    view = canvas.central_widget.add_view()

    camera = scene.cameras.TurntableCamera(elevation=0, azimuth=0, roll=90, distance=5)
    view.camera = camera

    view.add(XYZAxis())
    # image = canvas.render()

    # if sys.flags.interactive == 0:
    #     canvas.app.run()

    print(camera._get_rotation_tr())


if __name__ == "__main__":
    main()
