"""Just an experiment - I might split this out to another project"""
BINDCODE = 'bindcode'
BINDSYM = 'bindsym'


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
        lines = [
            l for l in lines if any(m in l for m in [BINDCODE, BINDSYM])]
        lines = [l for l in lines if not l.startswith(base.COMMENT_MARK)]
        return sorted(set(lines))

    def translate_bindings(self):
        """translate bindcode to bindsym assignments

        this need to be done the moment the information is asked because it
        depends on the currently acitve layout.
        """

    def write_bindings_info(self):
        """Write info in some format that can be nicely displayed"""


if __name__ == '__main__':
    # TODO use partials and account for modes
    # a naming convention would make this quite easy
    # mode-<modename>.conf -> bindings active in <modename>
    from i3configger import base, paths

    p = paths.get_i3wm_config_path() / 'config'
    b = Bindings(p.read_text())
    print('\n'.join(b.get_all_bindings()))
