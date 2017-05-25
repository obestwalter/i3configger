import logging
import pprint
import time
from pathlib import Path

from inotify import constants as ic
from inotify.adapters import Inotify

from i3configger import util
from i3configger.configger import I3Configger

log = logging.getLogger(__name__)


class Watchman:
    BUILD_DELAY = 1
    """If an IDE does monkey business (e.g. Jetbrains "safe write")
    more than one change might be triggered for each change.

    Using a small delay to not trigger to often.
    """

    """Watch a config directories and build/refresh/notify on changes"""
    MASK = (
        ic.IN_CREATE | ic.IN_ATTRIB | ic.IN_DELETE |
        ic.IN_MODIFY | ic.IN_CLOSE_WRITE |
        ic.IN_MOVED_FROM | ic.IN_MOVED_TO |
        ic.IN_DELETE_SELF | ic.IN_MOVE_SELF)
    """Tell inotify to trigger on changes"""

    def __init__(self, configgerArgs):
        self.configger = I3Configger(*configgerArgs)
        self.configPath = str(self.configger.sourcePath).encode()
        self.lastBuild = None
        self.lastFilePath = None
        self.errors = 0
        log.debug("initialized %s", self)

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__, pprint.pformat(self.__dict__))

    def watch(self):
        for event in self._get_events():
            self._process_event(event)

    def watch_guarded(self):
        for event in self._get_events():
            try:
                self._process_event(event)
            except:
                log.exception("I see dead calls ...")
                self.errors += 1
                if self.errors == 13:
                    log.critical("%s errors occurred, crashing", self.errors)
                    raise RuntimeError("%s: giving up" % self)

    def _get_events(self):
        inotify_watcher = Inotify()
        inotify_watcher.add_watch(self.configPath, mask=self.MASK)
        for event in inotify_watcher.event_gen():
            if not event:
                continue
            yield event

    def _process_event(self, event):
        header, typeNames, filePath = self._get_event_data(event)
        if self.needs_build(header, typeNames, filePath):
            log.info("%s triggered build", filePath)
            self.configger.build()
            self.lastBuild = time.time()
            self.lastFilePath = filePath
            util.IpcControl.refresh()
            util.IpcControl.notify_send('new config active')

    def _get_event_data(self, event):
        header, typeNames, watchPath, filename = event
        filePath = Path(watchPath.decode()) / filename.decode()
        log.debug("wd=%d|mask=%d|mask->names=%s|filePath=[%s]",
                  header.wd, header.mask, typeNames, filePath)
        return header, typeNames, filePath

    # noinspection PyUnusedLocal
    def needs_build(self, header, typeNames, filePath):
        if self.lastBuild and time.time() - self.lastBuild < self.BUILD_DELAY:
            log.debug("ignore %s changed too quick", filePath)
            return False
        if filePath.suffix != self.configger.suffix:
            return False
        if filePath != self.lastFilePath:
            log.debug("%s != %s", filePath, self.lastFilePath)
            return True
        return False
