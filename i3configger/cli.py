import logging
import sys
from argparse import ArgumentParser

from i3configger import __version__, daemonize
from i3configger.configger import build
from i3configger.util import IpcControl, LOG_PATH, configure_logging
from i3configger.watch import Watchman

log = logging.getLogger()


def parse_args():
    p = ArgumentParser('i3configger')
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('-v', action="count", help="raise verbosity")
    p.add_argument('--types', nargs='+', default=[],
                   help='activate type.<name>.conf files')
    p.add_argument('--reload', action="store_true", default=False,
                   help="reload i3 instead of restart (not i3bar update)")
    p.add_argument('--log', action="store_true", default=False,
                   help="log to %s" % LOG_PATH)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    g.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    g.add_argument('--kill', action="store_true", default=False,
                   help="exorcise daemon if running")
    return p.parse_args()


def main():
    args = parse_args()
    if args.daemon:
        daemonize.daemonize(args.v, args.log)
    if args.kill:
        daemonize.exorcise()
        return 0
    if args.reload:
        IpcControl.refresh = IpcControl.reload_i3
    else:
        configure_logging(verbosity=args.v, writeLog=args.log)
        builder = Watchman()
        if args.watch:
            try:
                builder.watch()
            except KeyboardInterrupt:
                sys.exit("bye")
        else:
            build(args.types)
            # todo need a way to refresh i3bar config without restarting i3
            IpcControl.refresh()


if __name__ == '__main__':
    sys.argv = ['dev-run', '--verbose', '--watch']
    sys.exit(main())
