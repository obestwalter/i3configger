import logging
import os
import sys
from pathlib import Path

import daemon  # type: ignore
import psutil  # type: ignore

from i3configger import base, build, exc, ipc, config
from i3configger.inotify_simple import INotify, flags

log = logging.getLogger(__name__)


_MASK = (
    flags.CREATE
    | flags.ATTRIB
    | flags.DELETE
    | flags.MODIFY
    | flags.CLOSE_WRITE
    | flags.MOVED_FROM
    | flags.MOVED_TO
    | flags.DELETE_SELF
    | flags.MOVE_SELF
)
"""Tell inotify to trigger on changes"""


def watch_guarded():
    while True:
        try:
            watch_unguarded()
        except exc.I3configgerException as e:
            ipc.communicate("WARNING", urgency="normal")
            log.warning(str(e))
        except Exception as e:
            ipc.communicate("ERROR", urgency="critical")
            log.error(str(e))


def watch_unguarded():
    cnf = config.I3configgerConfig(load=False)
    watcher = INotify()
    watcher.add_watch(str(cnf.partialsPath).encode(), mask=_MASK)
    log.debug(f"start watching {cnf.partialsPath}")
    while True:
        events = watcher.read(read_delay=50)
        log.debug(f"events: {[f'{e[3]}:m={e[1]}' for e in events]}")
        if not events:
            continue
        paths = [cnf.partialsPath / e[-1] for e in events]
        if any(p.suffix in [base.SUFFIX, ".json"] for p in paths):
            build.build_all()
            ipc.communicate(refresh=True)


def get_i3configger_process():
    """should always be max one, but you never know ..."""
    all_ = [p for p in psutil.process_iter() if p.name() == "i3configger"]
    others = [p for p in all_ if p.pid != os.getpid()]
    if len(others) == 1:
        return others[0]
    elif len(others) > 1:
        raise exc.I3configgerException(
            f"More than one i3configger running: {others}"
            f"If this happens again, please file an issue "
            f"and tell me how you did it."
        )


def daemonized(verbosity, logPath):
    process = get_i3configger_process()
    if process:
        sys.exit(f"i3configger already running ({process})")
    context = daemon.DaemonContext(working_directory=Path(__file__).parent)
    if verbosity > 2:
        # spew output to terminal from where daemon was started
        context.stdout = sys.stdout
        context.stderr = sys.stderr
    with context:
        base.configure_logging(verbosity, logPath, isDaemon=True)
        watch_guarded()


def exorcise():
    process = get_i3configger_process()
    if not process:
        raise exc.UserError("no daemon running - nothing to kill")
    process.kill()
    log.info(f"killed {process}")
