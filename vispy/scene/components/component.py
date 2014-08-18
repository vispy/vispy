from ..shaders import Function


class VisualComponent(object):
    """
    Base for classes that encapsulate some modular component of a Visual.

    These define Functions for extending the shader code as well as an
    activate() method that inserts these Functions into a program.

    VisualComponents may be considered friends of the Visual they are attached
    to; often they will need to access internal data structures of the Visual
    to make decisions about constructing shader components.
    """

    DRAW_PRE_INDEXED = 1
    DRAW_UNINDEXED = 2

    # Maps {'program_hook': 'GLSL code'}
    SHADERS = {}

    # List of shaders to automatically attach to the visual's program.
    # If None, then all shaders are attached.
    AUTO_ATTACH = None

    def __init__(self, visual=None):
        self._visual = None
        if visual is not None:
            self._attach(visual)

        self._funcs = dict([(name, Function(code))
                            for name, code in self.SHADERS.items()])

        # components that are required by this component
        self._deps = []

        # only detach when count drops to 0;
        # this is like a reference count for component dependencies.
        self._attach_count = 0

    @property
    def visual(self):
        """The Visual that this component is attached to."""
        return self._visual

    def _attach(self, visual):
        """Attach this component to a Visual. This should be called by the
        Visual itself.

        A component may only be attached to a single Visual. However, it may
        be attached _multiple times_ to the same visual.

        The default implementation of this method calls
        self._auto_attach_shaders() to generate the list of shader callbacks
        that should be added to the Visual's program.
        """
        if visual is not self._visual and self._visual is not None:
            raise Exception("Cannot attach component %s to %s; already "
                            "attached to %s" % (self, visual, self._visual))
        self._visual = visual
        self._attach_count += 1
        for hook in self._auto_attach_shaders():
            func = self._funcs[hook]
            try:
                visual._program.vert.add_callback(hook, func)
            except KeyError:
                visual._program.frag.add_callback(hook, func)
                
        for comp in self._deps:
            comp._attach(visual)

    def _detach(self):
        """Detach this component from its Visual. This should be called by the
        visual itself.

        If the component was attached
        multiple times, it must be detached the same number of times.
        """
        if self._attach_count == 0:
            raise Exception("Cannot detach component %s; not attached." % self)

        self._attach_count -= 1
        if self._attach_count == 0:
            for hook in self._auto_attach_shaders():
                func = self._funcs[hook]
                try:
                    self._visual._program.vert.remove_callback(hook, func)
                except KeyError:
                    self._visual._program.frag.remove_callback(hook, func)
            self._visual = None
            for comp in self._deps:
                comp._detach()

    def _auto_attach_shaders(self):
        """
        Return a list of shaders to automatically attach/detach
        """
        if self.AUTO_ATTACH is None:
            return self._funcs.keys()
        else:
            return self.AUTO_ATTACH

    @property
    def supported_draw_modes(self):
        """
        A set of the draw modes (either DRAW_PRE_INDEXED, DRAW_UNINDEXED, or
        both) currently supported by this component.

        DRAW_PRE_INDEXED indicates that the component may be used when the
        program uses an array of indices to determine the order of elements to
        draw from its vertex buffers (using glDrawElements).

        DRAW_UNINDEXED indicates that the component may be used when the
        program will not use an array of indices; rather, vertex buffers are
        processed in the order they appear in the buffer (using glDrawArrays).

        By default, this method returns a tuple with both values. Components
        that only support one mode must override this method.
        """
        # TODO: This should be expanded to include other questions, such as
        # whether the component supports geometry shaders.
        return set([self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED])

    def update(self):
        """
        Inform the attached visual that this component has changed.
        """
        if self.visual is not None:
            self.visual.update()

    def activate(self, program):
        """
        *program* is about to draw; attach to *program* all functions and
        data required by this component.
        """
        raise NotImplementedError
