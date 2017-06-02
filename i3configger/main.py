import logging
import sys
from pathlib import Path

from i3configger import (
    build, cli, config, daemonize, ipc, partials, paths, watch)

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.kill:
        daemonize.exorcise()
        return 0
    configPath = paths.get_my_config_path(args.config)
    if daemonize.get_other_i3configgers():
        if not args.message:
            sys.exit("i3configger already running. "
                     "Did you want to send a message?")
        # process and write the state and let watcher do the build
        log.info("watcher process is running - processing message")
        p = paths.Paths(configPath)
        config.State.process(p.state, partials.create(p.root), args.message)
        return 0
    # TODO merge args and conf (args override conf)
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    log.info("set i3 refresh method to %s", ipc.I3.refresh)
    ipc.Notify.set_notify_command(args.no_notify)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, configPath)
        return 0
    if args.watch:
        try:
            watch.Watchman(configPath).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    if args.load_config:
        p = paths.Paths(configPath)
        state = config.State.fetch_state(
            Path(args.load).expanduser(), partials.create(p.root))
        config.freeze(configPath, state)
    else:
        build.Builder(configPath).build()
        ipc.I3.refresh()
        ipc.StatusBar.refresh()
        ipc.Notify.send('new config active')


if __name__ == '__main__':
    # dev stuff
    sys.argv = ['dev', '-vvv']
    # sys.argv = ['dev', '-vvv', 'select-next', 'scheme']
    # sys.argv = ['dev', '-vvv', 'set', 'mode', 'dock']
    # sys.argv = ['dev', '-vvv', '--watch']
    sys.exit(main())
