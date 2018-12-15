import logging
import os
import sys
import tempfile
from pathlib import Path

from i3configger import exc

log = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", 0)
COMMENT_MARK = "#"
VAR_MARK = "$"
SET_MARK = "set"
SUFFIX = ".conf"
I3BAR = "i3bar"
"""reserved key for status bar template files"""
DEL = "del"
"""signal to delete a key in shadow or set"""


def configure_logging(verbosity: int, logPath: str, isDaemon=False):
    rootLogger = logging.getLogger()
    if logPath:
        logPath = Path(logPath).expanduser()
    else:
        name = "i3configger-daemon.log" if isDaemon else "i3configger.log"
        logPath = Path(tempfile.gettempdir()) / name
    if DEBUG:
        print(f"logging to {logPath}")
        level = logging.getLevelName("DEBUG")
    else:
        level = logging.getLevelName(
            {0: "ERROR", 1: "WARNING", 2: "INFO"}.get(verbosity, "DEBUG")
        )
    fmt = "%(asctime)s %(name)s:%(funcName)s:%(lineno)s " "%(levelname)s: %(message)s"
    if not rootLogger.handlers:
        logging.basicConfig(format=fmt, level=level)
    fileHandler = logging.FileHandler(logPath)
    fileHandler.setFormatter(logging.Formatter(fmt))
    fileHandler.setLevel(level)
    rootLogger.addHandler(fileHandler)


def get_version():
    """hide behind a wrapped function (slow and not a catastrophe if fails)"""
    try:
        from pkg_resources import get_distribution

        return get_distribution("i3configger").version
    except Exception:
        log.exception("fetching version failed")
        return "unknown"


def i3configger_excepthook(type_, value, traceback):
    """Make all exceptions look like a friendly error message :)"""
    if DEBUG or not isinstance(value, exc.I3configgerException):
        _REAL_EXCEPTHOOK(type_, value, traceback)
    else:
        sys.exit(f"{type(value)}: {value}")


_REAL_EXCEPTHOOK = sys.excepthook
sys.excepthook = i3configger_excepthook
