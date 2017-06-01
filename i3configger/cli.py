import argparse
import logging
from pathlib import Path

from i3configger import __version__, base, build, exc, config

log = logging.getLogger(__name__)


def process_command_line():
    parser = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args, message = _parse_known(parser)
    base.configure_logging(verbosity=args.v, logPath=args.log)
    check_sanity(message)
    args.config = Path(args.config).expanduser() if args.config else None
    args.message = message
    if message and any([args.daemon, args.kill, args.watch, args.init]):
        parser.error(
            "'commands and daemon/watch/init can't be used together: %s;%s" %
            (args, message))
    return args


def _parse_known(p):
    """Command line commands - all optional with [reasonable] defaults"""
    p.add_argument('--version', action='version',
                   version="%s %s" % (p.prog, __version__))
    p.add_argument('-v', action="count", help="raise verbosity", default=0)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--watch', action="store_true",
                   help="watch and build in foreground", default=False)
    g.add_argument('--daemon', action="store_true",
                   help="watch and build as daemon", default=False)
    g.add_argument('--kill', action="store_true", default=False,
                   help="exorcise daemon if running")
    p.add_argument('--i3-refresh-msg', action="store", default='restart',
                   choices=['restart', 'reload', 'nop'],
                   help="i3-msg to send after build")
    p.add_argument('--log', action="store", default=None,
                   help="i3configgerPath to where log should be stored")
    p.add_argument('-c', '--config', action="store",
                   default=None, help="i3configgerPath to config file")
    p.add_argument("message", help="message to send to i3configger", nargs="*")
    return p.parse_known_args()


def check_sanity(message):
    """Extract i3configger commands."""
    if not message:
        return
    log.debug("processing %s", message)
    command, *rest = message
    spec = config.Message.get_spec(command)
    if len(rest) != spec:
        raise exc.I3configgerException(
            f"message '{command}' needs {spec} args - got: {rest}")
    log.debug(f"{message} seem to be a legit message")
