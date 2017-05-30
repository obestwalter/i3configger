"""This is just a sketch ... """
raise NotImplementedError()

BINDCODE = 'bindcode'
BINDSYM = 'bindsym'


# set after build
class Bindings:
    """
    bindsym | bindcode
    [--release] [<Group>+][<Modifiers>+]<keysym> command

    [--release] [--border] [--whole-window] [<Modifiers>+]button<n> command
    """
    def __init__(self, lines):
        self.lines = lines

    def translate_bindings(self):
        """translate bindcode to bindsym assignments

        this need to be done the moment the information is asked because it
        depends on the currently acitve layout.
        """

    def write_bindings_info(self):
        """Write info in some format that can be nicely displayed"""
