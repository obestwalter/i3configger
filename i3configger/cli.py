import argparse
import logging
import sys

from i3configger import __version__, daemonize, defaults, util
from i3configger.configger import I3Configger
from i3configger.watch import Watchman

log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(
        'i3configger', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('-v', action="count", help="raise verbosity", default=0)
    p.add_argument('--sources', action="store",
                   default=defaults.SOURCES_PATH, help="path to sources")
    p.add_argument('--target', action="store",
                   default=defaults.TARGET_PATH,
                   help="path to main config file")
    p.add_argument('--suffix', action="store",
                   default=defaults.SOURCE_SUFFIX,
                   help="suffix of config source files")
    p.add_argument('--reload', action="store_true", default=False,
                   help="reload i3 instead of restart (not i3bar update)")
    p.add_argument('--logpath', action="store", default=defaults.LOG_PATH,
                   help="log to given path")
    g = p.add_mutually_exclusive_group()
    g.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    g.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    g.add_argument('--kill', action="store_true", default=False,
                   help="exorcise daemon if running")

    # fixme there has to be a better way - integrate into selectors
    p.add_argument('--statusmarker', action="store",
                   default=defaults.STATUS_MARKER,
                   help="prefix of status bar configurations")

    args, argv = p.parse_known_args()
    args.selectors = util.get_selectors(p, argv)
    util.dbg_print("initialized with %s", args)
    return args


def main():
    args = parse_args()
    configgerArgs = (args.sources, args.target, args.suffix, args.selectors,
                     args.statusmarker)
    if args.daemon:
        daemonize.daemonize(args.v, args.logpath, configgerArgs)
    if args.kill:
        daemonize.exorcise()
        return 0
    if args.reload:
        util.IpcControl.refresh = util.IpcControl.reload_i3
    util.configure_logging(verbosity=args.v, logpath=args.logpath)
    if args.watch:
        try:
            Watchman(configgerArgs).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        configger = I3Configger(*configgerArgs)
        configger.build()
        # TODO need a way to refresh i3bar config without restarting i3
        util.IpcControl.refresh()


if __name__ == '__main__':
    sys.exit(main())
