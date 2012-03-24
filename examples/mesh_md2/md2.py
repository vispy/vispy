'''
Created on 04/03/2012

@author: adam
'''

from pyglet.gl import *

from mesh.md2_mesh import MD2_Mesh


mesh = None
texture = None

def initialise_mesh():
    global mesh

    if mesh != None:
        return

    mesh = MD2_Mesh(
        r'examples/data/sydney.md2'
        )
    print 'Loading mesh'
    mesh.load()
    print 'Done'
    
    # load the texture
    #image = pyglet.image.load(
    #    #r'examples/data/sydney-scaled.bmp'
    #    )
    #texture = image.get_texture( rectangle = False )
    
    animation_time = 0
    
def render_mesh():
    global mesh
    # enable the texture
    #glEnable( texture.target )
    #glBindTexture( texture.target, texture.id )
    
    # render the md2 mesh
    mesh.render()
    
    # disable the texture
    #glDisable( texture.target )

