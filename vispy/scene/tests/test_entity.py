from vispy import scene
from vispy.app.backends import requires_non_glut
from vispy.app import Application
from vispy.util import transforms


@requires_non_glut()  # XXX only used b/c we can't trust GLUT not to crash
def test_show_entity():
    """Test showing an entity"""
    # Create a figure
    app = Application()
    fig = scene.CanvasWithScene(app=app)
    app.create()
    fig.size = 1, 1
    fig.show()
    camcontainer = scene.PixelCamera(fig.viewbox)
    camera = scene.ThreeDCamera(camcontainer)
    camera._fov = 90
    fig.viewbox.camera = camera
    pointscontainer = scene.Entity(fig.viewbox)
    scene.PointsEntity(pointscontainer, 1000)
    app.process_events()
    app.process_events()  # for good measure

    # Now do first-person
    camcontainer = scene.PixelCamera(fig.viewbox)
    camera = scene.FirstPersonCamera(camcontainer)
    camera.update_angles()
    fig.viewbox.camera = camera
    pointscontainer = scene.Entity(fig.viewbox)
    scene.PointsEntity(pointscontainer, 1000)
    app.process_events()
    app.process_events()  # for good measure

    # Now do 2D
    camcontainer = scene.PixelCamera(fig.viewbox)
    camera = scene.TwoDCamera(camcontainer)
    camera.xlim = -100, 500
    camera.ylim = -100, 500
    fig.viewbox.camera = camera
    pointscontainer = scene.Entity(fig.viewbox)
    scene.PointsEntity(pointscontainer, 1000)
    transforms.translate(camcontainer.transform, 50, 50)
    transforms.rotate(camcontainer.transform, 10, 0, 0, 1)
    app.process_events()
    app.process_events()  # for good measure

    fig.close()
    app.quit()
