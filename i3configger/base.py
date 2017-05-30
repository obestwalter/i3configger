import logging
import os
import sys

from cached_property import cached_property_with_ttl

from i3configger import exc

log = logging.getLogger(__name__)
DEBUG = os.getenv('DEBUG', 0)
VAR_MARK = '$'
SET_MARK = 'set'
SETTINGS_MARK = VAR_MARK + SET_MARK + '_'


def configure_logging(verbosity: int, logPath: str, isDaemon=False):
    rootLogger = logging.getLogger()
    if DEBUG:
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

if not DEBUG:
    # TODO add this when stable to speed things up?
    def timed_cached_property():
        return property
else:
    def timed_cached_property():
        return cached_property_with_ttl(1)

try:
    from IPython import embed
except ImportError:
    def embed():
        raise exc.I3configgerException("embed() needs Ipython installed")
