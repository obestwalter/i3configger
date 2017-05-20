import logging
import sys
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


def inotify_eventloop(sources, suffix, gather, build, refresh, notify):
    errors = 0
    # todo add logging file handler
    treeWatcher = InotifyTree(sources.encode(), mask=MASK)
    lastChange = time.time()
    lastFilename = None
    for event in treeWatcher.event_gen():
        try:
            if event:
                (header, typeNames, watchPath, filename) = event
                filename = filename.decode()
                if filename.endswith(suffix):
                    log.debug("wd=%d mask=%d MASK->NAMES=%s "
                              "WATCH-PATH=[%s] FILENAME=[%s]",
                              header.wd, header.mask, typeNames,
                              watchPath.decode(), filename)
                    if (filename == lastFilename
                            and time.time() - lastChange < BACKOFF_DELAY):
                        log.debug("ignore %s changed too quick", filename)
                        continue
                    log.info("%s changed -> %s", filename, build)
                    lastFilename = filename
                    lastChange = time.time()
                    fragments = gather()
                    log.debug("run %s with %s", build, fragments)
                    build(fragments)
                    log.debug("run %s", refresh)
                    refresh()
                    notify()
        except:
            # Very stupid attempt to handle case when running as daemon ...
            log.exception("tree watcher struggled")
            errors += 1
            if errors == 10:
                log.critical("too many errors, interrupting ...")
                sys.exit(1)
