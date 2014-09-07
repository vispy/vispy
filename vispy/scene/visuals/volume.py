from .modular_mesh import ModularMesh

class Volume(ModularMesh):
    def __init__(self, data, **kwds):
        super(Volume, self).__init__(**kwds)
