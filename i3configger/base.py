"""Basic names and functionality."""
import logging
import os
import sys
import tempfile
from pathlib import Path

from i3configger import exc

log = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", False)


def configure_logging(verbosity: int, logPath, isDaemon=False):
    rootLogger = logging.getLogger()
    verbosity = 3 if DEBUG else verbosity
    level = {0: "ERROR", 1: "WARNING", 2: "INFO"}.get(verbosity, "DEBUG")
    if logPath:
        logPath = Path(logPath).expanduser()
    else:
        name = "i3configger-daemon.log" if isDaemon else "i3configger.log"
        logPath = Path(tempfile.gettempdir()) / name
        if verbosity > 1:
            print(f"logging to {logPath} with level {level}", file=sys.stderr)
    fmt = "%(asctime)s %(name)s:%(funcName)s:%(lineno)s %(levelname)s: %(message)s"
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
    """Make own exceptions look like a friendly error message :)"""
    if DEBUG or not isinstance(value, exc.I3configgerException):
        _REAL_EXCEPTHOOK(type_, value, traceback)
    else:
        sys.exit(f"[FATAL] {type(value).__name__}: {value}")


_REAL_EXCEPTHOOK = sys.excepthook
sys.excepthook = i3configger_excepthook
