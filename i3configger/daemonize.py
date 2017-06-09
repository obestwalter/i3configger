import os
import sys
from pathlib import Path

import daemon
import psutil

from i3configger.watch import Watchman
from i3configger.base import configure_logging


def get_other_i3configgers():
    """should always be max one, but you never know ..."""
    others = [p for p in psutil.process_iter() if p.name() == 'i3configger']
    return [p for p in others if p.pid != os.getpid()]


def daemonize(verbosity, logPath, cnf):
    others = get_other_i3configgers()
    if others:
        sys.exit(f"i3configger already running ({others})")
    context = daemon.DaemonContext(working_directory=Path(__file__).parent)
    if verbosity:
        # spew output to terminal from where daemon was started
        context.stdout = sys.stdout
        context.stderr = sys.stderr
    with context:
        configure_logging(verbosity, logPath, isDaemon=True)
        Watchman(cnf).watch()


def exorcise():
    for process in get_other_i3configgers():
        print(f"killing {process.pid}")
        process.kill()
