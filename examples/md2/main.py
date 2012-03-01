'''
Created on 15/06/2011

@author: adam

TODO: use resource locations
http://www.pyglet.org/doc/programming_guide/loading_resources.html
'''

import math
import time
import random

import numpy
from pyglet.gl import *
import pyglet
# Disable error checking for increased performance
#pyglet.options['debug_gl'] = False

import maths.vector
import maths.quaternion
import maths.matrix33
from renderer.renderer import Renderer
from renderer.viewport import Viewport
from renderer.scene.camera_node import CameraNode
from renderer.scene.scene_node import SceneNode
from renderer.scene.render_callback_node import RenderCallbackNode
from renderer.fps_camera import FPS_Camera
from renderer.six_dof_camera import SixDOF_Camera
from input.keyboard import Keyboard
from input.mouse import Mouse
from mesh.md2_mesh import MD2_Mesh
#from mesh.oai_mesh import OAI_Mesh


# TODO: write a sierpinski drawing program using bit drawing
# http://en.wikipedia.org/wiki/File:Sierpinski_Racket_example.png

class Application( object ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
        # create our window
        config = pyglet.gl.Config(
            sample_buffers = 1,
            samples = 4,
            depth_size = 16,
            double_buffer = True
            )
        #config = None
        self.window = pyglet.window.Window(
            fullscreen = False,
            width = 1024,
            height = 768,
            config = config
            )
        
        # create our input devices
        self.keyboard = Keyboard( self.window )
        self.mouse = Mouse( self.window )
        
        # create our renderer
        self.renderer = Renderer( self.window )
        
        # setup our update loop the app
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        pyglet.clock.schedule_interval( self.step, self.update_delta )
        
        self.dt = 0.0
        self.total_time = 0.0
        
        # set the scene nodes to render debug nodes
        #SceneNode.render_debug_cube = True
        
        print "Rendering at %iHz" % int(frequency)
        
        self.setup()
    
    def setup( self ):
        # add a grid so we can see wtf we're doing
        self.grid_render_node = RenderCallbackNode(
            '/grid/rendernode',
            self.initialise_grid,
            self.render_grid
            )
        self.renderer.root.add_child( self.grid_render_node )
        
        # add a grid so we can see wtf we're doing
        self.mesh_node = RenderCallbackNode(
            '/mesh/rendernode',
            self.initialise_mesh,
            self.render_mesh
            )
        self.renderer.root.add_child( self.mesh_node )
        
        # create a camera
        camera = CameraNode(
            '/camera',
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = camera
        self.renderer.root.add_child( camera )
        
        #self.camera_controller = SixDOF_Camera()
        self.camera_controller = FPS_Camera()
        self.camera_controller.camera = self.camera
        
        # set it as the primary camera
        self.renderer.viewport.set_camera( camera )
        
        # move our nodes
        
        # the md2 is oriented at 90 degrees about X
        # re-orient the mesh
        #quat = maths.quaternion.set_to_rotation_about_x( -math.pi / 2.0 )
        #self.meshNode.rotate_quaternion( quat )
        quat = maths.quaternion.set_to_rotation_about_x( math.pi / 2.0 )
        self.mesh_node.rotate_quaternion( quat )
        
        
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        glEnable(GL_NORMALIZE)

        glLightfv(GL_LIGHT1, GL_AMBIENT, (GLfloat * 4)(*[0.5, 0.5, 0.5, 1.0]) )
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (GLfloat * 4)(*[1.0, 1.0, 1.0, 1.0]) )
        glLightfv(GL_LIGHT1, GL_POSITION, (GLfloat * 4)(*[0.0, 0.0, 15.0, 1.0]) )
        glEnable(GL_LIGHT1)
    
    def initialise_grid( self ):
        self.grid_display_list = generate_grid_display_list( (10, 10), (20, 20) )
    
    def render_grid( self ):
        # render the display list
        glCallList( self.grid_display_list )
    
    def initialise_mesh( self ):
        self.mesh = MD2_Mesh(
        #self.mesh = OAI_Mesh(
            r'examples/data/sydney.md2'
            )
        print 'Loading mesh'
        self.mesh.load()
        print 'Done'
        
        # load the texture
        #self.image = pyglet.image.load(
        #    #r'examples/data/sydney-scaled.bmp'
        #    )
        #self.texture = self.image.get_texture( rectangle = False )
        
        self.animation_time = 0
    
    def render_mesh( self ):
        # enable the texture
        #glEnable( self.texture.target )
        
        #glBindTexture( self.texture.target, self.texture.id )
        
        """
        self.animation_time += self.dt
        if self.animation_time > (1.0 / 20.0):
            frame = self.mesh.frame + 1
            frame %= self.mesh.frames
            self.mesh.frame = frame
            self.animation_time = 0.0
        """
        
        self.mesh.render()
        
        # enable the texture
        #glDisable( self.texture.target )
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # update the scene
        self.dt = dt
        self.total_time += dt        
        
        # update the Camera
        camera_speed = 40.0
        
        # movement
        if self.keyboard[ self.keyboard.keys.W ] or self.keyboard[ self.keyboard.keys.UP ]:
            # move forward
            self.camera_controller.translate_inertial_forward( camera_speed * dt )
            #self.camera_controller.translate_forward( camera_speed * dt )
        if self.keyboard[ self.keyboard.keys.S ] or self.keyboard[ self.keyboard.keys.DOWN ]:
            # move backward
            self.camera_controller.translate_inertial_backward( camera_speed * dt )
            #self.camera_controller.translate_backward( camera_speed * dt )
        if self.keyboard[ self.keyboard.keys.D ] or self.keyboard[ self.keyboard.keys.RIGHT ]:
            # move right
            self.camera_controller.translate_right( camera_speed * dt )
        if self.keyboard[ self.keyboard.keys.A ] or self.keyboard[ self.keyboard.keys.LEFT ]:
            # move right
            self.camera_controller.translate_left( camera_speed * dt )
        if self.keyboard[ self.keyboard.keys.SPACE ]:
            # move up
            self.camera_controller.translate_inertial_up( camera_speed * dt )
            #self.camera_controller.translate_up( camera_speed * dt )
        if self.keyboard[ self.keyboard.keys.LSHIFT ]:
            # move up
            self.camera_controller.translate_inertial_down( camera_speed * dt )
            #self.camera_controller.translate_down( camera_speed * dt )
        
        # camera rotation
        # FPS camera
        mouse_relative = self.mouse.relative_position
        mouse_speed = (1.0 / 3.0) * 0.02
        
        frame_pitch = math.pi * mouse_speed * mouse_relative[ 1 ]# * dt
        frame_yaw = -math.pi * mouse_speed * mouse_relative[ 0 ]# * dt
        
        invert_y = True
        if invert_y == True:
            frame_pitch = -frame_pitch
        
        self.camera_controller.orient( pitch = frame_pitch, yaw = frame_yaw )
        
        # reset our mouse relative position
        self.mouse.clear_delta()
        
        # set the ambient light
        glEnable( GL_LIGHTING )
        ambient = [ 0.8, 0.8, 0.8, 1.0 ]
        glAmbient = ( GLfloat * 4 )( *ambient )
        glLightModelfv( GL_LIGHT_MODEL_AMBIENT, glAmbient )
        
        # render the scene
        self.renderer.render()
        
        # display the frame buffer
        self.renderer.flip()
    

def generate_grid_display_list( cell_size, num_cells ):
    grid_dl = glGenLists( 1 );
    glNewList( grid_dl, GL_COMPILE )
    
    # disable the lighting
    glDisable( GL_LIGHTING )
    
    # TODO: use glPointParameter to automatically scale points
    # http://www.opengl.org/sdk/docs/man/xhtml/glPointParameter.xml
    glLineWidth( 1.0 )
    
    glBegin( GL_LINES )
    draw_grid( cell_size, num_cells )
    glEnd()
    
    glEndList()
    return grid_dl

def draw_grid( cell_size, num_cells ):
    # draw a white grid
    glColor3f( 1.0, 1.0, 1.0 )
    
    half_size = (
        (num_cells[ 0 ] / 2) * cell_size[ 0 ],
        (num_cells[ 1 ] / 2) * cell_size[ 1 ]
        )
    # draw our depth lines
    for x in xrange( num_cells[ 0 ] + 1 ):
        x_pos = float( -half_size[ 0 ] + (x * cell_size[ 0 ]) )
        
        glVertex3f( x_pos, 0.0, -half_size[ 1 ] )
        glVertex3f( x_pos, 0.0, +half_size[ 1 ] )
    
    # draw our width lines
    for z in xrange( num_cells[ 1 ] + 1 ):
        z_pos = float( -half_size[ 1 ] + (z * cell_size[ 1 ]) )
        
        glVertex3f( -half_size[ 1 ], 0.0, z_pos )
        glVertex3f( +half_size[ 1 ], 0.0, z_pos )
    


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

