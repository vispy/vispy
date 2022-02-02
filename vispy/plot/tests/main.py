# import datetime
# import random
#
# import numpy
# import pandas as pd
#
# import vispy.plot as vp
# from vispy.testing import (assert_raises, requires_application,
#                            run_tests_if_main)
# from vispy.visuals.axis import AxisVisual
# from unittest import mock
# from vispy import scene
# from vispy import app
# import numpy as np
#
#
# if __name__ == '__main__':
#
#     i = 1
#     def update(ev):
#         global i
#
#         i = i + 0.1
#
#         bar1.update_data(bottom=df['Bar1Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar1Height'][:int(i)].to_numpy(), width=0.8, color=(0.25, 0.8, 0.))
#         bar2.update_data(bottom=df['Bar2Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar2Height'][:int(i)].to_numpy(), width=0.3, color=(0.25, 0.8, 0.))
#         bar3.update_data(bottom=df['Bar3Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar3Height'][:int(i)].to_numpy(), width=0.3, color=(0.25, 0.8, 0.))
#         bar4.update_data(bottom=df['Bar4Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar4Height'][:int(i)].to_numpy(), width=0.8, color=(1, 0.1, 0.))
#         bar5.update_data(bottom=df['Bar5Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar5Height'][:int(i)].to_numpy(), width=0.3, color=(1, 0.1, 0.))
#         bar6.update_data(bottom=df['Bar6Bottom'][:int(i)].to_numpy(),
#                          height=df['Bar6Height'][:int(i)].to_numpy(), width=0.3, color=(1, 0.1, 0.))
#
#
#
#     df = pd.read_csv('aapl.csv')
#     # df = ray.get(dataserver.get_old_ohlc_data.remote(10, currency))
#
#     df['Index'] = df.index
#
#     canvas = scene.SceneCanvas(keys='interactive', vsync=False)
#     canvas.size = 1280, 720
#     canvas.show()
#
#     grid = canvas.central_widget.add_grid()
#     grid.padding = 10
#
#     # Create two ViewBoxes, place side-by-side
#     vb1 = grid.add_view(row=0, col=1, camera='panzoom')
#
#     x_axis1 = scene.AxisWidget(
#         orientation='bottom')
#     x_axis1.stretch = (1, 0.1)
#     grid.add_widget(x_axis1, row=1, col=1)
#     x_axis1.link_view(vb1)
#     y_axis1 = scene.AxisWidget(orientation='left')
#     y_axis1.stretch = (0.1, 1)
#     grid.add_widget(y_axis1, row=0, col=0)
#     y_axis1.link_view(vb1)
#
#     grid_lines1 = scene.visuals.GridLines(parent=vb1.scene)
#
#
#     df['green'] = np.where(df['AAPL.Close'] > df['AAPL.Open'], True, False)
#     df['red'] = np.where(df['AAPL.Close'] <= df['AAPL.Open'], True, False)
#     df['Bar1Height'] = np.where(df['green'] == True, df['AAPL.Close'] - df['AAPL.Open'], 0)
#     df['Bar2Height'] = np.where(df['green'] == True, df['AAPL.High'] - df['AAPL.Close'], 0)
#     df['Bar3Height'] = np.where(df['green'] == True, df['AAPL.Low'] - df['AAPL.Open'], 0)
#
#     df['Bar4Height'] = np.where(df['red'] == True, df['AAPL.Close'] - df['AAPL.Open'], 0)
#     df['Bar5Height'] = np.where(df['red'] == True, df['AAPL.High'] - df['AAPL.Open'], 0)
#     df['Bar6Height'] = np.where(df['red'] == True, df['AAPL.Low'] - df['AAPL.Close'], 0)
#
#     df['Bar1Bottom'] = np.where(df['green'] == True, df['AAPL.Open'], 0)
#     df['Bar2Bottom'] = np.where(df['green'] == True, df['AAPL.Close'], 0)
#     df['Bar3Bottom'] = np.where(df['green'] == True, df['AAPL.Open'], 0)
#     #
#     df['Bar4Bottom'] = np.where(df['red'] == True, df['AAPL.Open'], 0)
#     df['Bar5Bottom'] = np.where(df['red'] == True, df['AAPL.Open'], 0)
#     df['Bar6Bottom'] = np.where(df['red'] == True, df['AAPL.Close'], 0)
#
#     df['green'] = np.where(df['AAPL.Close'] > df['AAPL.Open'], True, False)
#     df['red'] = np.where(df['AAPL.Close'] <= df['AAPL.Open'], True, False)
#     df['Bar1Height'] = np.where(df['green'] == True, df['AAPL.Close'] - df['AAPL.Open'], 0)
#     df['Bar2Height'] = np.where(df['green'] == True, df['AAPL.High'] - df['AAPL.Close'], 0)
#     df['Bar3Height'] = np.where(df['green'] == True, df['AAPL.Low'] - df['AAPL.Open'], 0)
#
#     df['Bar4Height'] = np.where(df['red'] == True, df['AAPL.Close'] - df['AAPL.Open'], 0)
#     df['Bar5Height'] = np.where(df['red'] == True, df['AAPL.High'] - df['AAPL.Open'], 0)
#     df['Bar6Height'] = np.where(df['red'] == True, df['AAPL.Low'] - df['AAPL.Close'], 0)
#
#     df['Bar1Bottom'] = np.where(df['green'] == True, df['AAPL.Open'], 0)
#     df['Bar2Bottom'] = np.where(df['green'] == True, df['AAPL.Close'], 0)
#     df['Bar3Bottom'] = np.where(df['green'] == True, df['AAPL.Open'], 0)
#     #
#     df['Bar4Bottom'] = np.where(df['red'] == True, df['AAPL.Open'], 0)
#     df['Bar5Bottom'] = np.where(df['red'] == True, df['AAPL.Open'], 0)
#     df['Bar6Bottom'] = np.where(df['red'] == True, df['AAPL.Close'], 0)
#
#
#     print(df['Bar1Bottom'][:int(i)].to_numpy())
#
#     bar1 = scene.Bar(bottom=df['Bar1Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar1Height'][:int(i)].to_numpy(), width=0.8, color=(0.25, 0.8, 0.),
#                      parent=vb1.scene)
#     bar2 = scene.Bar(bottom=df['Bar2Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar2Height'][:int(i)].to_numpy(), width=0.3, color=(0.25, 0.8, 0.),
#                      parent=vb1.scene)
#     bar3 = scene.Bar(bottom=df['Bar3Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar3Height'][:int(i)].to_numpy(), width=0.3, color=(0.25, 0.8, 0.),
#                      parent=vb1.scene)
#     bar4 = scene.Bar(bottom=df['Bar4Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar4Height'][:int(i)].to_numpy(), width=0.8, color=(1, 0.1, 0.),
#                      parent=vb1.scene)
#     bar5 = scene.Bar(bottom=df['Bar5Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar5Height'][:int(i)].to_numpy(), width=0.3, color=(1, 0.1, 0.),
#                      parent=vb1.scene)
#     bar6 = scene.Bar(bottom=df['Bar6Bottom'][:int(i)].to_numpy(),
#                      height=df['Bar6Height'][:int(i)].to_numpy(), width=0.3, color=(1, 0.1, 0.),
#                      parent=vb1.scene)
#
#     timer = app.Timer()
#     timer.connect(update)
#     timer.start(0)
#
#     canvas.measure_fps()
#
#     vb1.camera.set_range()
#
#     canvas.measure_fps()
#     app.run()
