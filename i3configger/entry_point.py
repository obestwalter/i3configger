import logging
import sys

from i3configger import cli, base, build, daemonize, watch

log = logging.getLogger(__name__)


def main():
    args = cli.process_command_line()
    if args.daemon:
        daemonize.daemonize(args.v, args.logPath, args.build)
    if args.kill:
        daemonize.exorcise()
        return 0
    base.configure_logging(verbosity=args.v, logPath=args.logPath)
    base.IpcControl.set_i3_msg(args.i3_refresh_msg)
    log.info("set i3 refresh method to %s", base.IpcControl.refresh)
    if args.watch:
        try:
            watch.Watchman(args.build).watch()
        except KeyboardInterrupt:
            sys.exit("bye")
    else:
        build.Builder(*args.build).build()
        # TODO need a way to refresh i3bar config without restarting i3
        base.IpcControl.refresh()
        base.IpcControl.notify_send('new config active')


if __name__ == '__main__':
    sys.exit(main())
