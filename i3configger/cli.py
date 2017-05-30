import argparse
import logging
import tempfile
from pathlib import Path

from i3configger import __version__, exc, base, config
from i3configger.config import COMMAND, DEFAULT

log = logging.getLogger(__name__)


def process_command_line():
    parser = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args, command = _parse_known(parser)
    base.configure_logging(verbosity=args.v, logPath=args.log)
    args.sources = Path(args.sources)
    verify_command(command)
    args.build = (args.sources, Path(args.target), args.suffix, command)
    if command and (args.daemon or args.kill or args.watch):
        parser.error(
            'commands and daemon/watch actions not possible together: %s;%s' %
            (args, command))
    del args.target
    del args.suffix
    return args


def _parse_known(p):
    """Command line commands - all optional with [reasonable] defaults"""
    p.add_argument('--version', action='version',
                   version="%s %s" % (p.prog, __version__))
    p.add_argument('-v', action="count", help="raise verbosity", default=0)
    p.add_argument('--sources', action="store",
                   default=DEFAULT.sources, help="path to sources")
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
    _logs = str(Path(tempfile.gettempdir()) / 'i3configger.log')
    p.add_argument('--log', action="store", default=_logs,
                   help="path to where log should be stored")
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
