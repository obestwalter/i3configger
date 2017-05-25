import os
import sys
from pathlib import Path

import daemon
import psutil

from i3configger.watch import Watchman
from i3configger.util import configure_logging


def get_other_i3configgers():
    """should always be max one, but you never know ..."""
    others = [p for p in psutil.process_iter() if p.name() == 'i3configger']
    return [p for p in others if p.pid != os.getpid()]


def daemonize(verbosity, logpath, configgerArgs):
    others = get_other_i3configgers()
    if others:
        sys.exit("i3configger already running (%s)" % others)
    context = daemon.DaemonContext(
        working_directory=Path(__file__).parent
        # TODO check if this umask is ok umask=0o002
    )
    # todo handle signals properly
    # context.signal_map = {
    #     signal.SIGTERM: program_cleanup,
    #     signal.SIGHUP: 'terminate',
    #     signal.SIGUSR1: reload_program_config}
    if verbosity:
        # spew output to terminal from where daemon was started
        context.stdout = sys.stdout
        context.stderr = sys.stderr
    with context:
        configure_logging(verbosity, logpath, isDaemon=True)
        Watchman(configgerArgs).watch_guarded()


def exorcise():
    # todo some error handling
    for process in get_other_i3configgers():
        print("killing %s" % process.pid)
        process.kill()
