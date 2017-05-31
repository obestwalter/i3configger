import json
import logging
import os
import pprint
from pathlib import Path

from i3configger import exc, partials

log = logging.getLogger(__name__)
NAME = 'i3configger.json'


def init_i3configger(path):
    path = get_config_path(init=True, override=path)
    if path.exists():
        raise exc.ConfigError(f"{path} exists already, remove it first.")
    if path.is_dir():
            raise exc.ConfigError(f"{path} exists already, remove it first.")
    log.info("create a default i3configger configuration at %s", path)
    blueprint = Path(__file__).parent / NAME
    with open(blueprint) as f:
        I3configgerConfig.freeze(path, json.load(f))


def get_config_path(init=False, override=None):
    """Use same search order like i3 (no system stuff though).

    see: https://github.com/i3/i3/blob/4.13/libi3/get_config_path.c#L31
    """
    override = Path(override) if override else None
    standard = None
    traditional = Path('~/.i3/').expanduser()
    if traditional.exists():
        standard = traditional / NAME
    else:
        xdg = Path(os.getenv("XDG_CONFIG_HOME") or '~/.config/').expanduser()
        xdg /= 'i3'
        if xdg.exists():
            standard = xdg / NAME
    path = override or standard
    if init:
        if override and standard.exists():
            log.warning(f"You have a config already at {standard} "
                        f"that will be ignored for this run.")
        if path.exists():
            raise exc.ConfigError(f"{standard} exists already")
        if override and not override.parent.exists():
            raise exc.ConfigError(f"folder {override.parent} needs to exist")
    else:
        if not path.exists():
            msg = "Is i3 installed? I Can't find any config locations. " \
                  "Pass the i3configgerPath to your i3configger config directly or run " \
                  "'i3configger --init' first"
            raise exc.ConfigError(msg)
        if path.is_dir():
            raise exc.ConfigError(
                f"{path} needs to point to a file - not a directory")
    return path


class KEY:
    """Fixed keys in config to hold several config items"""
    BARS = "bars"
    DEFAULTS = "defaults"
    MARKER = "marker"
    MESSAGE = "message"
    NAME = "name"
    PARTIALS = "partials"
    SETTINGS = "settings"
    SELECTOR = "selector"
    SUFFIX = "suffix"
    TARGET = "target"
    TEMPLATE = "template"


class I3configgerConfig:
    def __init__(self, configPath, message: list=None, freeze=True):
        # TODO checks with helpful errors for screwed up configurations
        self.configPath = Path(configPath)
        self.payload = self.read(self.configPath)
        settings = self.payload[KEY.SETTINGS]
        self.name = settings[KEY.NAME]
        self._partials = settings[KEY.PARTIALS]
        self.partialsPath = Path(self._partials).expanduser()
        self.suffix = settings[KEY.SUFFIX]
        self._target = settings[KEY.TARGET]
        self.targetPath = Path(self._target).expanduser()
        msgMap = self.payload.get(KEY.MESSAGE, {})
        self.set = msgMap.get(Message.SET[0], {})
        self.select = msgMap.get(Message.SELECT[0], {})
        bars = self.payload.get(KEY.BARS, {})
        self.bars = self.resolve_bars(bars)
        log.debug("initialized config  %s", self)
        if message:
            Message.process(message, self)
            if freeze:
                log.info("freezing config to %s", self.configPath)
                self._freeze()

    def __str__(self):
        return "%s:\n%s" % (self.__class__.__name__,
                            pprint.pformat(vars(self.__class__)))

    def resolve_bars(self, incoming):
        defaults = incoming.get(KEY.DEFAULTS, {})
        bars = incoming.get(KEY.BARS)
        if not bars:
            return {}
        resolvedBars = {}
        for name, bar in self.bars.items():
            for defaultKey, defaultValue in defaults.items():
                if defaultKey not in bar:
                    bar[defaultKey] = defaultValue
            resolvedBars[name] = bar
        return resolvedBars

    def _freeze(self):
        self.freeze(self.configPath, self.payload)

    @staticmethod
    def read(path):
        if not path.exists():
            raise exc.ConfigError(f"No config found at {path}")
        with path.open() as f:
            log.info("read config from %s", path)
            payload = json.load(f)
            log.debug("use:\n", pprint.pformat(payload))
            return payload

    @staticmethod
    def freeze(path, obj):
        with open(path, 'w') as f:
            json.dump(obj, f, sort_keys=True, indent=4)


class Message:
    """Process a message to alter the configuration to be build.

    Tuple contains name and number of expected additional arguments
    """
    SELECT_NEXT = ("select-next", 1)
    SELECT_PREVIOUS = ("select-previous", 1)
    SELECT = ("select", 2)
    SET = ("set", 2)
    _ALL = [SELECT_NEXT, SELECT_NEXT, SELECT, SET]

    @staticmethod
    def _next(current, items: list):
        try:
            return items[items.index(current) + 1]
        except IndexError:
            return items[0]

    @staticmethod
    def _previous(current, items: list):
        try:
            return items[items.index(current) - 1]
        except IndexError:
            return items[-1]

    FUNC_MAP = {SELECT_NEXT: _next, SELECT_PREVIOUS: _previous}

    @classmethod
    def get_spec(cls, message):
        for c in cls._ALL:
            if c[0] == message:
                return c[1]
        raise exc.MessageError(f"unknown message: {message}")

    @classmethod
    def process(cls, message: list, cnf: I3configgerConfig):
        command, key, *rest = message
        value = rest[0] if rest else None
        log.debug(f"sending message {message} to {cnf}")
        if command == cls.SET:
            cnf.set[key] = value
        else:
            prts = partials.create(cnf.partialsPath, cnf.suffix)
            prts = partials.select(prts, cnf.select)
            if command in [cls.SELECT_NEXT, cls.SELECT_PREVIOUS]:
                candidates = partials.find(prts, key)
                if not candidates:
                    raise exc.MessageError(f"No candidates for {message}")
                current = cnf.select.get(key) or candidates[-1]
                new = cls.FUNC_MAP[command](current, candidates)
                cnf.select[key] = new.value
            elif command == cls.SELECT:
                candidate = partials.find(prts, key, value)
                if not candidate:
                    raise exc.MessageError(f"No candidate for {message}")
                cnf.select[key] = candidate.value
