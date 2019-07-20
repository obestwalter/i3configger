"""WARNING Just an experiment - please ignore this."""
from i3configger import config

BINDCODE = "bindcode"
BINDSYM = "bindsym"


class Bindings:
    """
    bindsym | bindcode
    [--release] [<Group>+][<Modifiers>+]<keysym> command

    [--release] [--border] [--whole-window] [<Modifiers>+]button<n> command
    """

    def __init__(self, content):
        self.content = content

    def get_all_bindings(self):
        lines = [l.strip() for l in self.content.splitlines()]
        lines = [l for l in lines if any(m in l for m in [BINDCODE, BINDSYM])]
        lines = [l for l in lines if not l.startswith(config.MARK.COMMENT)]
        return sorted(set(lines))

    def translate_bindings(self):
        """translate bindcode to bindsym assignments

        this need to be done the moment the information is asked because it
        depends on the currently active layout.
        """
        raise NotImplementedError()

    def write_bindings_info(self):
        """Write info in some format that can be nicely displayed"""
        raise NotImplementedError()


if __name__ == "__main__":
    # use partials and account for modes
    # a naming convention would make this quite easy
    # mode-<modename>.conf -> bindings active in <modename>
    p = config.I3configgerConfig().targetPath
    b = Bindings(p.read_text())
    print("\n".join(b.get_all_bindings()))
