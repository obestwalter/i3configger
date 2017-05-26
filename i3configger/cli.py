import argparse
import logging
import sys

from i3configger import __version__, daemonize, defaults, utils
from i3configger.configger import I3Configger
from i3configger.watch import Watchman

log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
    p.add_argument('--i3-refresh-msg', action="store", default='none',
                   help="i3-msg to send after build (restart, reload, none)")
    p.add_argument('--log-path', action="store", default=defaults.LOG_PATH,
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
    args.selectors = utils.get_selector_map(p, argv)
    utils.dbg_print("initialized with %s", args)
    return args


def main():
    args = parse_args()
    configgerArgs = (args.sources, args.target, args.suffix, args.selectorMap,
                     args.statusmarker)
    if args.daemon:
        daemonize.daemonize(args.v, args.log_path, configgerArgs)
    if args.kill:
        daemonize.exorcise()
        return 0
    utils.configure_logging(verbosity=args.v, logPath=args.log_path)
    utils.IpcControl.set_i3_msg(args.i3_refresh_msg)
    log.info("set i3 refresh method to %s", utils.IpcControl.refresh)
    if args.watch:
        try:
            Watchman(configgerArgs).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        configger = I3Configger(*configgerArgs)
        configger.build()
        # TODO need a way to refresh i3bar config without restarting i3
        utils.IpcControl.refresh()


if __name__ == '__main__':
    sys.exit(main())
