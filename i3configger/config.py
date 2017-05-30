import json
import logging
import pprint
from pathlib import Path

from i3configger import exc

log = logging.getLogger(__name__)
CNF_NAME = 'i3configger.json'
_DEFAULT_CNF_PATH = Path(__file__).parent


def get_config(sources) -> dict:
    path = Path(sources).expanduser() / CNF_NAME
    if sources != _DEFAULT_CNF_PATH and not path.exists():
        log.info("create a new config from default at %s", path)
        freeze_config(sources, cnf)
        return cnf
    log.info("read config from %s", path)
    with open(path) as f:
        return json.load(f)


cnf = get_config(_DEFAULT_CNF_PATH)


def freeze_config(sources, obj):
    path = Path(sources).expanduser() / CNF_NAME
    with open(path, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=4)


class DEFAULT:
    """defaults (can be overridden from command line or config file)

    command line wins over config file, wins over defaults
    """
    _default = cnf['default']
    sources = _default['sources']
    suffix = _default['suffix']
    target = _default['target']


class KEY:
    """Fixed keys in config to hold several config items"""
    BAR_TEMPLATE = "bar-template"
    BARS = "bars"
    DEFAULTS = "defaults"
    MARKER = "marker"
    SETTINGS = "settings"
    SOURCE = "source"
    TARGET = "target"


class COMMAND:
    """commands that can be issued from the command line,

    Tuple contains name and number of expected additional arguments
    """
    NEXT = ("next", 1)
    PREVIOUS = ("previous", 1)
    SELECT = ("select", 2)
    SET = ("set", 2)
    _ALL = [NEXT, PREVIOUS, SELECT, SET]

    @classmethod
    def get_spec(cls, command):
        for c in cls._ALL:
            if c[0] == command:
                return c[1]
        raise exc.I3configgerException(f"unknown command: {command}")


class I3configgerConfig:
    def __init__(self, sourcesPath):
        self.payload = self._read(Path(sourcesPath) / CNF_NAME)
        self.configure_main()
        self.configure_i3status()

    @property
    def hasStatusConfig(self):
        return self.payload.get("status") is not None

    # TODO
    def configure_main(self):
        pass

    def configure_i3status(self):
        if KEY.BARS not in self.payload:
            log.info("nothing to do - no bars defined in %s", self.payload)
            return
        self.bars = self.payload[KEY.BARS]
        settings = {KEY.MARKER: "status", KEY.BAR_TEMPLATE: "tpl",
                    KEY.TARGET: DEFAULT.I3_PATH}
        if KEY.SETTINGS in self.payload:
            for key, value in self.payload[KEY.SETTINGS].items():
                settings[key] = value
        log.info("using settings: %s", pprint.pformat(settings))
        self.defaults = settings
        if KEY.DEFAULTS in self.payload:
            self.defaults.update(self.payload[KEY.DEFAULTS])
        else:
            log.info("no bar defaults - make sure you have everything in bars")
            self.defaults = {}
        for _, bar in self.bars.items():
            for defaultKey, defaultValue in self.defaults.items():
                if defaultKey not in bar:
                    bar[defaultKey] = defaultValue
        self.marker = settings[KEY.MARKER]
        self.template = settings[KEY.BAR_TEMPLATE]
        self.target = settings[KEY.TARGET]

    def _read(self, path):
        if not path.exists():
            log.info("no config file found at %s", path)
            return
        with path.open() as f:
            log.info("read config from %s", path)
            return json.load(f)

    def create(self, path, settings):
        with path.open('w') as f:
            return json.dump(settings, f)
