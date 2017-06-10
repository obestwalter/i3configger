import logging
import sys

from i3configger import (
    build, cli, exc, daemonize, ipc, partials, paths, message, watch)

log = logging.getLogger(__name__)


def main():
    """Wrap main to show own exceptions wo traceback in normal use."""
    args = cli.process_command_line()
    try:
        _main(args)
    except exc.I3configgerException as e:
        if args.v > 2:
            raise
        sys.exit(e)


def _main(args):
    if args.kill:
        daemonize.exorcise()
        return 0
    configPath = paths.get_my_config_path(args.config)
    if args.message:
        p = paths.Paths(configPath)
        prts = partials.create(p.root)
        message.process(p.messages, prts, args.message)
    if daemonize.get_daemon_process():
        if not args.message:
            sys.exit("Already running - did you mean to send a message?")
        log.info("let the daemon do the work")
        return 0
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    log.info("set i3 refresh method to %s", ipc.I3.refresh)
    ipc.Notify.set_notify_command(args.notify)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, configPath)
        return 0
    if args.watch:
        try:
            watch.forever(configPath).watch()
        except KeyboardInterrupt:
            sys.exit("interrupted by user")
    build.build_all(configPath)
    ipc.I3.refresh()
    ipc.StatusBar.refresh()
    ipc.Notify.send('new config active')
