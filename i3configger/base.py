import logging
import os
import sys
import tempfile
from pathlib import Path

from i3configger import exc

log = logging.getLogger(__name__)
DEBUG = os.getenv('DEBUG', 0)
VAR_MARK = '$'
SET_MARK = 'set'
SUFFIX = '.conf'
SETTINGS_MARK = VAR_MARK + SET_MARK + '_'


def configure_logging(verbosity: int, logPath: str, isDaemon=False):
    rootLogger = logging.getLogger()
    _log = str(Path(tempfile.gettempdir()) / 'i3configger.log')
    logPath = Path(logPath).expanduser() if logPath else _log
    if DEBUG:
        print('logging to %s' % logPath)
        level = 'DEBUG'
    else:
        level = logging.getLevelName(
            {0: 'ERROR', 1: 'WARNING', 2: 'INFO'}.get(verbosity, 'DEBUG'))
    fmt = ('%(asctime)s %(name)s:%(funcName)s:%(lineno)s '
           '%(levelname)s: %(message)s')
    if isDaemon:
        logging.basicConfig(filename=logPath, format=fmt, level=level)
    else:
        logging.basicConfig(format=fmt, level=level)
        fileHandler = logging.FileHandler(logPath)
        fileHandler.setFormatter(logging.Formatter(fmt))
        fileHandler.setLevel(level)
        rootLogger.addHandler(fileHandler)


def i3configger_excepthook(type_, value, traceback):
    if DEBUG or not isinstance(value, exc.I3configgerException):
        _REAL_EXCEPTHOOK(type_, value, traceback)
    else:
        sys.exit("%s: %s" % (value.__class__.__name__, value))


_REAL_EXCEPTHOOK = sys.excepthook
sys.excepthook = i3configger_excepthook
