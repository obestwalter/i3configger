import logging
import sys

from i3configger import (
    build, cli, daemonize, ipc, partials, paths, state, watch)

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.kill:
        daemonize.exorcise()
        sys.exit()
    configPath = paths.get_my_config_path(args.config)
    if args.message:
        p = paths.Paths(configPath)
        state.process(p.state, partials.create(p.root), args.message)
    if daemonize.get_other_i3configgers():
        if not args.message:
            sys.exit("i3configger already running. "
                     "Did you want to send a message?")
        log.info("watcher process is running - processing message")
        sys.exit()
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    log.info("set i3 refresh method to %s", ipc.I3.refresh)
    ipc.Notify.set_notify_command(args.notify)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, configPath)
        sys.exit()
    if args.watch:
        try:
            watch.Watchman(configPath).watch()
        except KeyboardInterrupt:
            sys.exit("interrupted by user")
    build.build_all(configPath)
    ipc.I3.refresh()
    ipc.StatusBar.refresh()
    ipc.Notify.send('new config active')
