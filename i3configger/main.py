import logging
import sys

from i3configger import cli, build, config, daemonize, ipc, watch, paths

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.kill:
        daemonize.exorcise()
        return 0
    ipc.I3.set_msg_type(args.i3_refresh_msg)
    configPath = paths.get_my_config_path(args.config)
    cnf = config.I3configgerConfig(configPath, args.message)
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
    sys.argv = ['dev', '-vvv', 'select-next', 'scheme']
    sys.exit(main())
