import logging
import os
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path

import daemon
import psutil

from i3configger import __version__
from i3configger.lib import I3Configger, IniConfig, IpcControl

log = logging.getLogger()


def configure_logging(verbose, logfile=None, daemon=False):
    level = logging.DEBUG if verbose else logging.INFO
    fmt = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    if daemon:
        if not logfile:
            logfile = Path(tempfile.gettempdir()) / 'i3configger.log'
        logging.basicConfig(filename=logfile, format=fmt, level=level)
        return
    logging.basicConfig(stream=sys.stdout, format=fmt, level=level)
    if not logfile:
        return
    fileHandler = logging.FileHandler(Path(logfile).expanduser())
    fileHandler.setFormatter(logging.Formatter(fmt))
    fileHandler.setLevel(level)
    log.addHandler(fileHandler)
    log.debug("logging to %s", logfile)


def parse_args():
    p = ArgumentParser('i3configger')
    p.add_argument('--ini-path', action="store",
                   help="path to i3configger.ini", default=None)
    p.add_argument('--verbose', action="store_true", default=False)
    p.add_argument('--reload', action="store_true", default=False,
                   help="reload i3 instead of restart (not i3bar update)")
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    p.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    p.add_argument('--kill', action="store_true",
                   help="kill the deamon if it is running", default=False)
    return p.parse_args()


def get_foreign_processes():
    procs = [p for p in psutil.process_iter() if p.name() == 'i3configger']
    return [p for p in procs if p.pid != os.getpid()]


def daemonize(buildDefs, maxerrors, verbose, logfile=None):
    foreignProcesses = get_foreign_processes()
    if foreignProcesses:
        sys.exit("i3configger already running (%s)" % foreignProcesses)
    context = daemon.DaemonContext(
        working_directory=Path(__file__).parent,
        # TODO check if this umask is ok
        umask=0o002)
    # todo handle signals properly
    # context.signal_map = {
    #     signal.SIGTERM: program_cleanup,
    #     signal.SIGHUP: 'terminate',
    #     signal.SIGUSR1: reload_program_config}
    if verbose:
        # spew output to terminal from where daemon was started
        context.stdout = sys.stdout
        context.stderr = sys.stderr
    with context:
        configure_logging(verbose, logfile, daemon=True)
        i3configger = I3Configger(buildDefs, maxerrors)
        i3configger.watch_guarded()


def main():
    args = parse_args()
    cnf = IniConfig(IniConfig.get_config(args.ini_path))
    log.debug("config: %s", cnf)
    if args.kill:
        # todo some error handling
        for process in get_foreign_processes():
            print("killing %s" % process.pid)
            process.kill()
        return 0
    if args.reload:
        IpcControl.refresh = IpcControl.reload_i3
    if args.daemon:
        daemonize(cnf.buildDefs, cnf.maxerrors, args.verbose, cnf.logfile)
    else:
        configure_logging(args.verbose, cnf.logfile)
        i3Configger = I3Configger(cnf.buildDefs, cnf.maxerrors)
        if args.watch:
            try:
                i3Configger.watch()
            except KeyboardInterrupt:
                sys.exit("bye")
        else:
            i3Configger.build()
            # todo need a way to refresh i3bar config without restarting i3
            IpcControl.refresh()
        return 0


if __name__ == '__main__':
    sys.argv = ['dev-run', '--verbose', '--watch']
    sys.exit(main())
