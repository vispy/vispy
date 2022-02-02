# import numpy as np
# from vispy import scene, app
#
# if __name__ == "__main__":
#     canvas = scene.SceneCanvas(keys='interactive', vsync=False)
#     canvas.size = 1280, 720
#     canvas.show()
#
#     grid = canvas.central_widget.add_grid()
#     grid.padding = 10
#
#     vb1 = grid.add_view(row=0, col=1, camera='panzoom')
#     vb2 = grid.add_view(row=2, col=1, camera='panzoom')
#
#     x_axis1 = scene.AxisWidget(orientation='bottom')
#     x_axis1.stretch = (1, 0.1)
#     grid.add_widget(x_axis1, row=1, col=1)
#     x_axis1.link_view(vb1)
#     y_axis1 = scene.AxisWidget(orientation='left')
#     y_axis1.stretch = (0.1, 1)
#     grid.add_widget(y_axis1, row=0, col=0)
#     y_axis1.link_view(vb1)
#
#     y_axis2 = scene.AxisWidget(orientation='left')
#     y_axis2.stretch = (0.1, 1)
#     grid.add_widget(y_axis2, row=2, col=0)
#     y_axis2.link_view(vb2)
#     x_axis2 = scene.AxisWidget(orientation='top')
#     x_axis2.stretch = (1, 0.1)
#     grid.add_widget(x_axis2, row=2, col=1)
#     x_axis2.link_view(vb2)
#
#     grid_lines1 = scene.visuals.GridLines(parent=vb1.scene)
#     grid_lines2 = scene.visuals.GridLines(parent=vb2.scene)
#
#     h = 10
#     length = 101
#     bottom = np.random.randint(h, size=length)
#
#     height1 = bottom + np.random.randint(h, size=length)
#
#     height2 = np.arange(length)
#
#     scene.Bar(height=height1, bottom=bottom, width=0.8, color=(0.25, 0.8, 0.),
#               parent=vb1.scene)
#
#     scene.Bar(height=height2, width=0.8, color=(1, 0, 0.),
#               parent=vb2.scene)
#
#     # Set subplot
#     vb1.camera.link(vb2.camera, axis="x")
#
#     vb1.camera.set_range()
#     vb2.camera.set_range()
#
#     canvas.measure_fps()
#     app.run()
