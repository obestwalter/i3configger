import logging
import os
import sys
from pathlib import Path

import daemon
import psutil

from i3configger import watch, exc
from i3configger.base import configure_logging

log = logging.getLogger(__name__)


def get_daemon_process():
    """should always be max one, but you never know ..."""
    all_ = [p for p in psutil.process_iter() if p.name() == 'i3configger']
    others = [p for p in all_ if p.pid != os.getpid()]
    if len(others) == 1:
        return others[0]
    elif len(others) > 1:
        raise exc.I3configgerException(
            f"More than one i3configger running: {others}"
            f"If this happens again, please file an issue "
            f"and tell me how you did it.")


def daemonize(verbosity, logPath, configPath):
    others = get_daemon_process()
    if others:
        sys.exit(f"i3configger already running ({others})")
    context = daemon.DaemonContext(working_directory=Path(__file__).parent)
    if verbosity > 2:
        # spew output to terminal from where daemon was started
        context.stdout = sys.stdout
        context.stderr = sys.stderr
    with context:
        configure_logging(verbosity, logPath, isDaemon=True)
        watch.forever(configPath)


def exorcise():
    process = get_daemon_process()
    if not process:
        raise exc.UserError("no daemon running - nothing to kill")
    process.kill()
    log.info(f"killed {process}")
