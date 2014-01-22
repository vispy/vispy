from vispy import scene
from vispy.app.backends import requires_pyglet
from vispy.app import Application
from vispy.util import transforms


@requires_pyglet()  # XXX only used b/c we can't trust GLUT not to crash
def test_show_entity():
    """Test showing an entity"""
    # Create a figure
    app = Application()
    app.use('Pyglet')
    #canvas = Canvas(title='me', app=app, show=True, position=[0, 0, 1, 1])
    fig = scene.CanvasWithScene(app=app)
    fig.size = 1, 1
    fig.show()
    camcontainer = scene.PixelCamera(fig.viewbox)
    camera = scene.ThreeDCamera(camcontainer)
    camera._fov = 90
    fig.viewbox.camera = camera
    pointscontainer = scene.Entity(fig.viewbox)
    scene.PointsEntity(pointscontainer, 1000)
    fig.on_paint(None)

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
    fig.on_paint(None)

    fig.close()
    app.quit()
