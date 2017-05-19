import logging
import time

from inotify import constants as ic
from inotify.adapters import InotifyTree

log = logging.getLogger(__name__)

BACKOFF_DELAY = 0.1
"""If an IDE does monkey business with the files (e.g. Jetbrains "safe write")
more than one change is triggered for each change. 

Using a small delay to not trigger to often.
"""

MASK = (ic.IN_MODIFY | ic.IN_CLOSE_WRITE | ic.IN_MOVED_FROM | ic.IN_MOVED_TO
        | ic.IN_CREATE | ic.IN_DELETE | ic.IN_DELETE_SELF | ic.IN_MOVE_SELF)
"""Trigger only on changes"""


def inotify_eventloop(sources, suffix, gather_func, build_func):
    # todo add logging file handler
    try:
        treeWatcher = InotifyTree(sources.encode(), mask=MASK)
        lastChange = time.time()
        lastFilename = None
        for event in treeWatcher.event_gen():
            if event:
                (header, typeNames, watchPath, filename) = event
                filename = filename.decode()
                log.debug(
                    "WD=(%d) MASK=(%d) COOKIE=(%d) LEN=(%d) MASK->NAMES=%s "
                    "WATCH-PATH=[%s] FILENAME=[%s]",
                    header.wd, header.mask, header.cookie, header.len,
                    typeNames, watchPath.decode('utf-8'), filename)
                if filename.endswith(suffix):
                    if (filename == lastFilename
                            and time.time() - lastChange < BACKOFF_DELAY):
                        log.debug("ignore %s changed too quick", filename)
                        continue
                    log.info("%s changed -> build new config", filename)
                    lastFilename = filename
                    lastChange = time.time()
                    build_func(fragments=gather_func())
    except:
        log.exception("tree watcher struggled")
