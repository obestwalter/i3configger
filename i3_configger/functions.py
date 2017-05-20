import subprocess
import time
from pathlib import Path


def gather_fragments(sources, suffix):
    """:returns: list of pathlib.Path"""
    return [path for path in sorted([d for d in Path(sources).iterdir()])
            if path.suffix == suffix]


def build_config(destination, msg, fragments):
    msg = '# %s (%s) #' % (msg, time.asctime())
    sep = "#" * len(msg)
    out = ["%s\n%s\n%s" % (sep, msg, sep)]
    out.extend(["# %s\n\n%s" % (f, f.read_text()) for f in fragments])
    Path(destination).write_text('\n\n'.join(out))


def i3_reload():
    subprocess.check_call(['i3-msg', 'reload'])


def i3_restart():
    subprocess.check_call(['i3-msg', 'restart'])


def notify():
    subprocess.check_call(
        ['notify-send', '-a', 'i3-configger',
         '-t', '1', '-u', 'low', "config replaced"])
