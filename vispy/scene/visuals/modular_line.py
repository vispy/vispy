from .modular_visual import ModularVisual


class ModularLine(ModularVisual):
    """
    Displays multiple line segments.
    """
    def __init__(self, parent=None, pos=None, color=None, z=0.0,
                 mode='line_strip', **kwds):
        super(ModularLine, self).__init__(parent=parent, **kwds)

        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        if mode in ('lines', 'line_strip'):
            self._primitive = mode
        else:
            raise ValueError("Invalid line mode '%s'; must be 'lines' or "
                             "'line-strip'.")

        if pos is not None or color is not None or z is not None:
            self.set_data(pos=pos, color=color, z=z)

    def set_data(self, pos=None, **kwds):
        kwds['index'] = kwds.pop('edges', kwds.get('index', None))
        kwds.pop('width', 1)  # todo: do something with width
        super(ModularLine, self).set_data(pos, **kwds)
