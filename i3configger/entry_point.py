import logging
import sys

from i3configger import cli, base, build, config, daemonize, ipc, watch

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.init:
        config.init(args.config)
        return 0
    if args.kill:
        daemonize.exorcise()
        return 0
    cnf = config.I3configgerConfig(config.get_config_path(args.config))
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, args.build)
        return 0
    log.info("set i3 refresh method to %s", ipc.I3.refresh)
    if args.watch:
        try:
            watch.Watchman(cnf).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        build.Builder(*args.build).build()
        ipc.I3.refresh()
        ipc.StatusBar.refresh()
        ipc.Notify.send('new config active')


if __name__ == '__main__':
    sys.argv = ['dev', '-vvv']
    sys.exit(main())
