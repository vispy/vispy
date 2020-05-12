import numpy as np

from vispy import scene

import sys

from vispy.scene.visuals import XYZAxis

from vispy.scene.visuals import SurfacePlot

def create_cylinder(center, radius, length):
    """ Creates the data of a cylinder oriented along z axis whose center, radius and length are given as inputs
        Based on the example given at: https://stackoverflow.com/a/49311446/2602319
    """
    z = np.linspace(0, length, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = radius * np.cos(theta_grid) + center[0]
    y_grid = radius * np.sin(theta_grid) + center[1]
    z_grid = z_grid + center[2]
    return x_grid, y_grid, z_grid

def create_paraboloid(center, radius, a, b, c):
    """
    Creates the data of a paraboloid whose center, radius and a, b, c parameters are given as inputs
    """
    # Generate the grid in cylindrical coordinates
    r = np.linspace(0, radius, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    R, THETA = np.meshgrid(r, theta)
    
    # Convert to rectangular coordinates
    x_grid, y_grid = R * np.cos(THETA), R * np.sin(THETA)
    
    z_grid = c * ((x_grid / a) ** 2 + (y_grid / b) ** 2)  # Elliptic paraboloid
    
    
    return x_grid + center[0], y_grid + center[1], z_grid + center[2]
    
def create_sphere(center, radius):
    """
    Creates the data of a sphere whose center, and radius are given as inputs
    """
    # Generate the grid in spherical coordinates
    # Names of the spherical coordinate axes according to ISO convention
    theta = np.linspace(0, np.pi, 50)
    phi = np.linspace(0, 2 * np.pi, 50)
    PHI, THETA = np.meshgrid(phi, theta)
    RHO = radius  # Size of the sphere
    
    # Convert to cartesian coordinates
    x_grid = (RHO * np.sin(THETA) * np.cos(PHI)) + center[0]
    y_grid = (RHO * np.sin(THETA) * np.sin(PHI)) + center[1]
    z_grid = (RHO * np.cos(THETA)) + center[2]
    
    return x_grid, y_grid, z_grid


# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

view = canvas.central_widget.add_view()

camera = scene.cameras.TurntableCamera(fov=60, parent=view.scene)
view.camera = camera

# Add a 3D axis
XYZAxis(parent=view.scene)

x_grid, y_grid, z_grid = create_paraboloid((0, 0, 3), 2, 6, 3, 3)
SurfacePlot(x_grid, y_grid, z_grid, color="aquamarine", parent=view.scene)

x_grid, y_grid, z_grid = create_cylinder((0, 0, 0), 1, 3)
SurfacePlot(x_grid, y_grid, z_grid, color="lightgreen", parent=view.scene)

x_grid, y_grid, z_grid = create_sphere((0, 0, 4), 0.5)
SurfacePlot(x_grid, y_grid, z_grid, color='lightseagreen', parent=view.scene)


if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
