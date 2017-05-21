import signal
import sys
import time
from pathlib import Path

import daemon
import lockfile


def initial_program_setup():
    print("initial setup")


def do_main_program():
    while True:
        print("working, working, workging ...")
        time.sleep(2)


def reload_program_config():
    print("reloaded")


def program_cleanup():
    print("all clean")


def daemonize():
    context = daemon.DaemonContext(
        working_directory=Path(__file__).parent,
        umask=0o002,
        pidfile=lockfile.FileLock('spam.pid'),
    )

    context.signal_map = {
        signal.SIGTERM: program_cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: reload_program_config,
    }

    context.stdout = sys.stdout
    context.stderr = sys.stderr

    # mail_gid = grp.getgrnam('mail').gr_gid
    # context.gid = mail_gid

    with context:
        do_main_program()
