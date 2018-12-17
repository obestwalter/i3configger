import argparse
import logging
import sys

from i3configger import base, build, config, exc, ipc, message, watch

log = logging.getLogger(__name__)


def main():
    """Wrap main to show own exceptions wo traceback in normal use.

    FIXME check if an what kind of sense this makes together with exception hook
    """
    args = cli.process_command_line()
    try:
        _main(args)
    except exc.I3configgerException as e:
        if args.v > 2:
            raise
        sys.exit(e)


def _main(args):
    config.ensure_i3_configger_sanity()
    cnf = config.I3configgerConfig()
    ipc.configure(cnf)
    base.configure_logging(verbosity=args.v, logPath=cnf.payload["main"]["log"])
    if args.version:
        print(f"i3configger {base.get_version()}")
        return 0
    if args.kill:
        watch.exorcise()
        return 0
    if args.message:
        message.save(args.message)
    if watch.get_i3configger_process():
        if not args.message:
            sys.exit("FATAL: already running - did you mean to send a message?")
        log.info("let the running process do the work")
        return 0
    if args.daemon:
        watch.daemonized(args.v, args.log)
    elif args.watch:
        try:
            watch.watch_guarded()
        except KeyboardInterrupt:
            sys.exit("interrupted by user")
    else:
        build.build_all()
        ipc.communicate(refresh=True)


def process_command_line():
    parser = argparse.ArgumentParser(
        "i3configger", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    args = _parse_args(parser)
    config.cliMainOverrideMap = vars(args)
    if args.message and any([args.daemon, args.kill, args.watch]):
        parser.error(
            "message and daemon/watch can't be used together. "
            "Start the watcher process first and then you can send "
            "messages in following calls."
        )
    return args


def _parse_args(p):
    """Command line commands - all optional with [reasonable] defaults"""
    p.add_argument(
        "--version", action="store_true", help="show version information and exit"
    )
    p.add_argument("-v", action="count", help="raise verbosity", default=0)
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--watch",
        action="store_true",
        help="watch and build in foreground",
        default=False,
    )
    g.add_argument(
        "--daemon", action="store_true", help="watch and build as daemon", default=False
    )
    g.add_argument(
        "--kill", action="store_true", default=False, help="exorcise daemon if running"
    )
    p.add_argument(
        "--i3-refresh-msg",
        action="store",
        default="reload",
        choices=["restart", "reload", "nop"],
        help="i3-msg to send after build",
    )
    p.add_argument(
        "--notify",
        action="store_true",
        default=False,
        help="show build notification via notify-send",
    )
    p.add_argument(
        "--log",
        action="store",
        default=None,
        help="i3configgerPath to where log should be stored",
    )
    p.add_argument("message", help="message to send to i3configger", nargs="*")
    return p.parse_args()
