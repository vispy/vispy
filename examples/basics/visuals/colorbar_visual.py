from vispy import app
from vispy import gloo
from vispy.visuals.transforms import STTransform, TransformSystem
from vispy.visuals import ColorBarVisual
from vispy.color import Color


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        pos = 800, 0
        halfdim = 500, 80

        self.bar = ColorBarVisual(pos, halfdim, cmap="ice", clim=(0.0, 1.0))
        self.transform = STTransform(scale=(1, 1), translate=(0, 0))

        self.transform_system = TransformSystem(self)
        self.transform_system.visual_to_document = self.transform

        self.show()

    def on_draw(self, event):
        gloo.clear(color=Color("white"))
        self.bar.draw(self.transform_system)


win = Canvas()
app.run()
