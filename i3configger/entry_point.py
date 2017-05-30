import logging
import sys

from i3configger import cli, base, build, config, daemonize, ipc, watch

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.kill:
        daemonize.exorcise()
        return 0
    config.cnf.update(config.get_config(args.sources))
    ipc.I3msg.set_msg_type(args.i3_refresh_msg)
    if args.daemon:
        daemonize.daemonize(args.v, args.log, args.build)
        return 0
    log.info("set i3 refresh method to %s", ipc.I3msg.refresh)
    if args.watch:
        try:
            watch.Watchman(args.build).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        build.Builder(*args.build).build()
        # TODO need a way to refresh i3bar config without restarting i3
        ipc.I3msg.refresh()
        ipc.Notify.send('new config active')


if __name__ == '__main__':
    sys.argv = ['dev', '-vvv']
    sys.exit(main())
