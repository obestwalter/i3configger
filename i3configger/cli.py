import argparse
import logging
from pathlib import Path

from i3configger import __version__, base

log = logging.getLogger(__name__)


def process_command_line():
    parser = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = _parse_args(parser)
    base.configure_logging(verbosity=args.v, logPath=args.log)
    args.config = Path(args.config).expanduser() if args.config else None
    if args.message and any([args.daemon, args.kill, args.watch]):
        parser.error("message and daemon/watch can't be used together. "
                     "Start the watcher process first and then you can send "
                     "messages in following calls.")
    return args


def _parse_args(p):
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
    p.add_argument('--i3-refresh-msg', action="store", default='reload',
                   choices=['restart', 'reload', 'nop'],
                   help="i3-msg to send after build")
    p.add_argument('--notify', action="store_true", default=False,
                   help="show build notification via notify-send")
    p.add_argument('--log', action="store", default=None,
                   help="i3configgerPath to where log should be stored")
    p.add_argument('-c', '--config', action="store",
                   default=None, help="i3configgerPath to config file")
    p.add_argument("message", help="message to send to i3configger", nargs="*")
    return p.parse_args()
