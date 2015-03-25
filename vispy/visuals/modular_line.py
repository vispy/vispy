from .modular_visual import ModularVisual


class ModularLine(ModularVisual):
    """
    Displays multiple line segments.
    """
    def __init__(self, pos=None, color=None, z=0.0,
                 mode='line_strip', **kwargs):
        super(ModularLine, self).__init__(**kwargs)

        glopts = kwargs.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        glopts = kwargs.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        if mode in ('lines', 'line_strip'):
            self._primitive = mode
        else:
            raise ValueError("Invalid line mode '%s'; must be 'lines' or "
                             "'line-strip'.")

        if pos is not None or color is not None or z is not None:
            self.set_data(pos=pos, color=color, z=z)

    def set_data(self, pos=None, **kwargs):
        kwargs['index'] = kwargs.pop('edges', kwargs.get('index', None))
        kwargs.pop('width', 1)  # todo: do something with width
        super(ModularLine, self).set_data(pos, **kwargs)
