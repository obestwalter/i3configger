import argparse
import logging
from pathlib import Path

from i3configger import __version__, base, exc
from i3configger.build import COMMAND

log = logging.getLogger(__name__)


def process_command_line():
    parser = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args, command = _parse_known(parser)
    base.configure_logging(verbosity=args.v, logPath=args.log)
    verify_command(command)
    args.config = Path(args.config).expanduser() if args.config else None
    args.command = command
    if command and any([args.daemon, args.kill, args.watch, args.init]):
        parser.error(
            "'commands and daemon/watch/init can't be used together: %s;%s" %
            (args, command))
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
                   help="path to where log should be stored")
    p.add_argument('-c', '--config', action="store",
                   default=None, help="path to config file")
    p.add_argument('--init', action="store_true", default=False,
                   help="create default config in your i3 folder or at path"
                        "passed in with -c|--config (this will never be found"
                        "automatically then and has to be passed with every "
                        "call to i3configger).")
    p.add_argument("command", help="command to give to i3configger", nargs="*")
    return p.parse_known_args()


def verify_command(args):
    """Extract i3configger commands."""
    if not args:
        return
    log.debug("processing %s", args)
    command, *rest = args
    spec = COMMAND.get_spec(command)
    if len(rest) != spec:
        raise exc.I3configgerException(
            f"command '{command}' needs {spec} args - got: {rest}")
    log.debug(f"{args} seem to be a legit command")
