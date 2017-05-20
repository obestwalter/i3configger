import logging
import subprocess
import time
from pathlib import Path

from inotify import constants as ic
from inotify.adapters import InotifyTree

log = logging.getLogger(__name__)


class I3Configger:
    """Watch a directory tree and build/refresh/notify on changes"""
    BACKOFF_DELAY = 0.1
    """If an IDE does monkey business (e.g. Jetbrains "safe write")
    more than one change might be triggered for each change.

    Using a small delay to not trigger to often.
    """

    MASK = (
        ic.IN_CREATE | ic.IN_ATTRIB | ic.IN_DELETE |
        ic.IN_MODIFY | ic.IN_CLOSE_WRITE |
        ic.IN_MOVED_FROM | ic.IN_MOVED_TO |
        ic.IN_DELETE_SELF | ic.IN_MOVE_SELF)
    """Tell inotify to trigger on changes"""

    MSG = "i3 config created at %s with i3configger"

    def __init__(self, cnf):
        """
        :param cnf: the config for the configger not the i3 config :)
        """
        self.msg = cnf.msg
        self.destination = Path(cnf.destination)
        self.sources = Path(cnf.sources)
        self.suffixes = cnf.suffixes
        self.maxErrors = cnf.maxErrors
        self.tree = InotifyTree(cnf.sources.encode(), mask=self.MASK)
        self.lastChange = time.time()
        self.lastFilename = None
        self.errors = 0

    def watch(self):
        for event in self.tree.event_gen():
            if not event:
                continue
            self.process_event(event)

    def watch_guarded(self):
        for event in self.tree.event_gen():
            if not event:
                continue
            try:
                self.process_event(event)
            except:
                log.exception("I see dead calls ...")
                self.errors += 1
                if self.errors == self.maxErrors:
                    log.critical("%s errors occurred, crashing", self.errors)
                    raise RuntimeError("%s: giving up" % self)

    def process_event(self, event):
        (header, typeNames, watchPath, filename) = event
        watchPath = Path(watchPath.decode())
        filename = Path(filename.decode())
        log.debug("wd=%d mask=%d MASK->NAMES=%s "
                  "WATCH-PATH=[%s] FILENAME=[%s]",
                  header.wd, header.mask, typeNames,
                  watchPath, filename)
        # todo handle IN_DELETE_SELF and IN_MOVE_SELF (error?)
        if self.decide(header, typeNames, watchPath, filename):
            log.info("%s triggered processing", filename)
            self.build()
            self.reload()
            self.notify()
            self.lastFilename = filename
            self.lastChange = time.time()

    # noinspection PyUnusedLocal
    def decide(self, header, typeNames, watchPath, filename):
        if not self.matches(filename):
            return False
        if not self.lastChange:
            return True
        if filename != self.lastFilename:
            log.debug("%s != %s", filename, self.lastFilename)
            return True
        if time.time() - self.lastChange < self.BACKOFF_DELAY:
            log.debug("ignore %s changed too quick", filename)
            return False
        return False

    def gather(self):
        """:returns: list of pathlib.Path"""
        return [p for p in sorted([d for d in self.sources.iterdir()])
                if self.matches(p)]

    def build(self):
            msg = '# %s (%s) #' % (self.msg, time.asctime())
            sep = "#" * len(msg)
            out = ["%s\n%s\n%s" % (sep, msg, sep)]
            out.extend(
                ["# %s\n\n%s" % (f, f.read_text()) for f in self.gather()])
            self.destination.write_text('\n'.join(out))

    def reload(self):
        subprocess.check_call(['i3-msg', 'reload'])

    def restart(self):
        subprocess.check_call(['i3-msg', 'restart'])

    def notify(self):
        subprocess.check_call(
            ['notify-send', '-a', 'i3configger',
             '-t', '1', '-u', 'low', "config replaced"])

    def matches(self, path):
        return any(path.suffix == suffix for suffix in self.suffixes)
