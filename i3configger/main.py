import logging
import sys

from i3configger import (
    cli, build, config, daemonize, ipc, watch, paths, exc, partials)

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.kill:
        daemonize.exorcise()
        return 0
    configPath = paths.get_my_config_path(args.config)
    cnf = config.I3configgerConfig(configPath, args.message)
    if daemonize.get_other_i3configgers():
        if not args.message:
            raise exc.I3configgerException(
                "already running. Did you want to send a message?")
        # process and write the state and let watcher do the build
        log.info("watcher process is running - processing message")
        prts = partials.create(cnf.partialsPath)
        config.State.process(cnf.statePath, prts, args.message)
        return 0
    # TODO merge args and conf (args override conf)
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    ipc.Notify.set_notify_command(args.no_notify)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, cnf)
        return 0
    log.info("set i3 refresh method to %s", ipc.I3.refresh)
    if args.watch:
        try:
            watch.Watchman(cnf).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        build.Builder(cnf).build()
        ipc.I3.refresh()
        ipc.StatusBar.refresh()
        ipc.Notify.send('new config active')


if __name__ == '__main__':
    # sys.argv = ['dev', '-vvv']
    # sys.argv = ['dev', '-vvv', 'select-next', 'scheme']
    sys.argv = ['dev', '-vvv', 'set', 'mode', 'dock']
    sys.exit(main())
