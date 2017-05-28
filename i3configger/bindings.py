BINDCODE = 'bindcode'
BINDSYM = 'bindsym'


# TODO set after rendering
class Bindings:
    """
    bindsym | bindcode
    [--release] [<Group>+][<Modifiers>+]<keysym> command

    [--release] [--border] [--whole-window] [<Modifiers>+]button<n> command
    """
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.dict)

    def translate_bindings(self):
        """translate bindcode to bindsym assignments

        this need to be done the moment the information is asked because it
        depends on the currently acitve layout.
        """

    def write_bindings_info(self):
        """Write info in some format that can be nicely displayed"""

    @property
    def dict(self):
        context = {}
        for line in self.lines:
            if not self.is_binding(line):
                continue
            maxsplit = 3 if '--release' in line else 2
            bindType, shortcut, binding = line.split(maxsplit=maxsplit)
            context["%s:%s" % (bindType, shortcut)] = binding
        return context

    @staticmethod
    def is_binding(line):
        return line.startswith(BINDSYM) or line.startswith(BINDCODE)

    @property
    def bindings(self):
        exp = 0
        for line in self.prunedLines:
            if Bindings.is_binding(line):
                exp += 1
        bindings = Bindings(self.prunedLines)
        if len(bindings) != exp:
            raise exc.ParseError("expected %s bindings - got %s for %s",
                                 exp, len(bindings), self.clean)
        return bindings

