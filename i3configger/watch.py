import logging

from i3configger import base, build, ipc
from i3configger.inotify_simple import INotify, flags

log = logging.getLogger(__name__)


_MASK = (flags.CREATE | flags.ATTRIB | flags.DELETE | flags.MODIFY |
         flags.CLOSE_WRITE | flags.MOVED_FROM | flags.MOVED_TO |
         flags.DELETE_SELF | flags.MOVE_SELF)
"""Tell inotify to trigger on changes"""


def forever(configPath):
    partialsPath = configPath.parent
    watcher = INotify()
    watcher.add_watch(str(partialsPath).encode(), mask=_MASK)
    log.debug(f"initialized {watcher}")
    while True:
        events = watcher.read(read_delay=50)
        log.debug(f"events: {[f'{e[3]}:m={e[1]}' for e in events]}")
        if not events:
            continue
        paths = [partialsPath / e[-1] for e in events]
        if any(p.suffix in [base.SUFFIX, '.json'] for p in paths):
            build.build_all(configPath)
            ipc.I3.refresh()
            ipc.StatusBar.refresh()
            ipc.Notify.send('new config active')
