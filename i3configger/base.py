import json
import logging
import os
import pprint
import subprocess
import sys
import tempfile
from pathlib import Path

from cached_property import cached_property_with_ttl

from i3configger import exc

log = logging.getLogger(__name__)
DEBUG = os.getenv('DEBUG', 0)
PROJECT_PATH = Path(__file__).parents[1]
LOG_PATH = Path(tempfile.gettempdir()) / 'i3configger.log'
I3_PATH = Path('~/.i3').expanduser()
SOURCES_PATH = I3_PATH / 'config.d'
TARGET_PATH = I3_PATH / 'config'
SOURCE_SUFFIX = '.conf'
VAR_MARK = '$'
SET_MARK = 'set'
SETTINGS_MARK = VAR_MARK + SET_MARK + '_'


# FIXME adapt to new style
def get_selectors(parser, argv):
    log.debug("found extra arguments, reading into selector map ...")
    selectorMap = {}
    leftovers = []
    marker = '--select-'
    markerLen = len(marker)
    for arg in argv:
        if not arg.startswith(marker) or '=' not in arg:
            leftovers.append(arg)
        else:
            key, value = arg[markerLen:].split('=')
            selectorMap[key] = value
    if leftovers:
        hint = "hint: selectors must use the form: --select-<key>=<value>"
        parser.error(
            'unrecognized arguments: %s\n%s' % ('; '.join(argv), hint))
    return selectorMap


class I3Status:
    MARKER = "marker"
    TEMPLATE = "template"
    SOURCE = "source"
    TARGET = "target"
    DEFAULT_SETTINGS = {MARKER: "i3status", TEMPLATE: "tpl", TARGET: "~/.i3"}
    BARS = "bars"
    SETTINGS = "settings"
    DEFAULTS = "defaults"
    I3STATUS = "i3status"
    FILE_NAME = I3STATUS + ".json"

    def __init__(self, sourcePath):
        path = Path(sourcePath) / self.FILE_NAME
        log.debug("use %s", path)
        if not path.exists():
            log.info("no bar settings - nothing to do")
            return
        with path.open() as f:
            payload = json.load(f)
        if self.BARS not in payload:
            log.info("nothing to do - no bars defined in %s", payload)
            return
        self.bars = payload[self.BARS]
        settings = self.DEFAULT_SETTINGS
        if self.SETTINGS in payload:
            for key, value in payload[self.SETTINGS].items():
                settings[key] = value
        log.info("using settings: %s", pprint.pformat(settings))
        self.defaults = settings
        if self.DEFAULTS in payload:
            self.defaults.update(payload[self.DEFAULTS])
        else:
            log.info("no bar defaults - make sure you have everything in bars")
            self.defaults = {}
        for _, bar in self.bars.items():
            for defaultKey, defaultValue in self.defaults.items():
                if defaultKey not in bar:
                    bar[defaultKey] = defaultValue
        self.marker = settings[self.MARKER]
        self.template = settings[self.TEMPLATE]
        self.target = settings[self.TARGET]

    def __bool__(self):
        return hasattr(self, 'bars')


class IpcControl:
    @classmethod
    def set_i3_msg(cls, which):
        cls.refresh = {
            'restart': cls.restart_i3,
            'reload': cls.reload_i3,
        }.get(which, cls.nop)

    @classmethod
    def reload_i3(cls):
        if cls._send_i3_msg('reload'):
            cls.notify_send("reloaded i3")

    @classmethod
    def restart_i3(cls):
        if cls._send_i3_msg('restart'):
            cls.notify_send("restarted i3")

    @classmethod
    def nop(cls):
        pass

    refresh = restart_i3

    @classmethod
    def _send_i3_msg(cls, msg):
        # todo use Adaephons i3 library
        cmd = ['i3-msg', msg]
        try:
            output = subprocess.check_output(cmd).decode()
            if '"success":true' in output:
                return True
            cls.notify_send("%s: %s" % (cmd, output), urgency='critical')
            return False
        except subprocess.CalledProcessError as e:
            if msg == 'restart' and e.returncode == 1:
                log.debug("[IGNORE] exit 1 is ok for restart")
                return True

    @classmethod
    def notify_send(cls, msg, urgency='low'):
        subprocess.check_call([
            'notify-send', '-a', 'i3configger', '-t', '1', '-u', urgency, msg])


def configure_logging(verbosity, logPath, isDaemon=False):
    rootLogger = logging.getLogger()
    if DEBUG:
        level = 'DEBUG'
    else:
        level = logging.getLevelName(
            {0: 'ERROR', 1: 'WARNING', 2: 'INFO'}.get(verbosity, 'DEBUG'))
    fmt = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    if isDaemon:
        logging.basicConfig(filename=str(logPath), format=fmt, level=level)
    else:
        logging.basicConfig(format=fmt, level=level)
        fileHandler = logging.FileHandler(str(logPath))
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
