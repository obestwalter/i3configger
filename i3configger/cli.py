import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from i3configger import __version__
from i3configger.as_daemon import daemonize
from i3configger.lib import IniConfig, I3Configger, IpcControl

log = logging.getLogger()


def configure_logging(verbose, logfile):
    level = logging.DEBUG if verbose else logging.INFO
    fmt = '%(asctime)s %(name)s %(levelname)s: %(message)s'
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
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    p.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    p.add_argument('--kill', action="store_true",
                   help="kill the deamon if it is running", default=False)
    return p.parse_args()


def main():
    args = parse_args()
    cnf = IniConfig(IniConfig.get_config(args.ini_path))
    configure_logging(args.verbose, cnf.logfile)
    log.debug("config: %s", cnf)
    if args.kill:
        raise NotImplementedError  # TODO
    i3Configger = I3Configger(cnf.buildDefs, cnf.maxerrors)
    if args.watch:
        i3Configger.watch()
    elif args.daemon:
        daemonize()
        # todo make work with real code
        #daemonize(I3Configger)
    else:
        i3Configger.build()
        # todo is there a way to reload the status bar without restarting i3?
        IpcControl.reload_i3()


if __name__ == '__main__':
    sys.argv = ['dev', '--verbose', '--watch']
    sys.exit(main())
