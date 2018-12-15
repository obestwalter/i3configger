import logging
import sys

from i3configger import base, build, cli, config, exc, ipc, message, watch

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


# TODO turn watch, daemon and kill also into commands?


def _main(args):
    config.ensure_i3_configger_sanity()
    cnf = config.I3configgerConfig()
    ipc.configure(cnf)
    base.configure_logging(verbosity=args.v, logPath=cnf.payload["main"]["log"])
    if args.version:
        print(f"i3configger {base.get_version()}")
        return 0
    if args.kill:
        watch.exorcise()
        return 0
    if args.message:
        message.save(args.message)
    if watch.get_i3configger_process():
        if not args.message:
            sys.exit("FATAL: already running - did you mean to send a message?")
        log.info("let the running process do the work")
        return 0
    if args.daemon:
        watch.daemonized(args.v, args.log)
    elif args.watch:
        try:
            watch.watch_guarded()
        except KeyboardInterrupt:
            sys.exit("interrupted by user")
    else:
        build.build_all()
        ipc.communicate(refresh=True)
