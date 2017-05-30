import argparse
import logging
from pathlib import Path

import sys

from i3configger import __version__, exc
from i3configger.config import DEFAULT, COMMAND

log = logging.getLogger(__name__)


def process_command_line():
    parser = argparse.ArgumentParser(
        'i3configger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args, unknowns = _parse_known(parser)
    args.logPath = Path(args.logs)
    args.sourcePath = Path(args.sources)
    command, unknowns = verify_command(unknowns)
    args.build = (Path(args.sources), Path(args.target), args.suffix, command)
    if command and (args.daemon or args.kill or args.watch):
        parser.error(
            'commands and daemon/watch actions not possible together: %s;%s' %
            (args, command))
    if unknowns:
        parser.error('unrecognized arguments: %s' % ('; '.join(unknowns)))
    del args.sources
    del args.target
    del args.suffix
    return args


def _parse_known(p):
    """Command line commands - all optional with [reasonable] defaults"""
    p.add_argument('--version', action='version',
                   version="%s %s" % (p.prog, __version__))
    p.add_argument('-v', action="count", help="raise verbosity", default=0)
    p.add_argument('--sources', action="store",
                   default=DEFAULT.SOURCES_PATH, help="path to sources")
    p.add_argument('--target', action="store", default=DEFAULT.TARGET_PATH,
                   help="path to main config file")
    p.add_argument('--suffix', action="store",
                   default=DEFAULT.SOURCE_SUFFIX,
                   help="suffix of config source files")
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
    p.add_argument('--log', action="store", default=DEFAULT.LOG_PATH,
                   help="path to where log should be stored")
    p.add_argument("command", help="command to give to i3configger", nargs="*")
    return p.parse_known_args()


def verify_command(args):
    """Extract i3configger commands."""
    log.debug("processing %s", args)
    if not args:
        return
    command, *rest = args
    spec = COMMAND.get_spec(command)
    if len(rest) != spec:
        raise exc.I3configgerException(
            f"command '{command}' needs {spec} args - got: {rest}")
    log.debug(f"{args} seem to be a legit command")
