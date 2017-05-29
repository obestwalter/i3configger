import argparse
import logging
import sys
from pathlib import Path

from i3configger import __version__, base, daemonize, build, watch

log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--version', action='version',
                   version="%s %s" % (p.prog, __version__))
    p.add_argument('-v', action="count", help="raise verbosity", default=0)
    p.add_argument('--sources', action="store",
                   default=base.SOURCES_PATH, help="path to sources")
    p.add_argument('--targetPath', action="store",
                   default=base.TARGET_PATH,
                   help="path to main config file")
    p.add_argument('--suffix', action="store",
                   default=base.SOURCE_SUFFIX,
                   help="suffix of config source files")
    p.add_argument('--i3-refresh-msg', action="store", default='none',
                   help="i3-msg to send after build (restart, reload, none)")
    p.add_argument('--log-path', action="store", default=base.LOG_PATH,
                   help="log to given path")
    g = p.add_mutually_exclusive_group()
    g.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    g.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    g.add_argument('--kill', action="store_true", default=False,
                   help="exorcise daemon if running")
    args, argv = p.parse_known_args()
    args.sources = Path(args.sources)
    args.target = Path(args.target)
    args.log_path = Path(args.log_path)
    args.selectorMap = base.get_selector_map(p, argv)
    args.configger = (args.sources, args.target, args.suffix, args.selectorMap)
    return args


def main():
    cnf = parse_args()
    if cnf.daemon:
        daemonize.daemonize(cnf.v, cnf.log_path, cnf.configger)
    if cnf.kill:
        daemonize.exorcise()
        return 0
    base.configure_logging(verbosity=cnf.v, logPath=cnf.log_path)
    base.IpcControl.set_i3_msg(cnf.i3_refresh_msg)
    log.info("set i3 refresh method to %s", base.IpcControl.refresh)
    if cnf.watch:
        try:
            watch.Watchman(cnf.configger).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        build.Builder(*cnf.configger).build_all()
        # TODO need a way to refresh i3bar config without restarting i3
        base.IpcControl.refresh()


if __name__ == '__main__':
    sys.exit(main())
