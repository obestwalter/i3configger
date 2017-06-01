import json
import logging
import os
import pprint
from pathlib import Path

from i3configger import exc, partials

log = logging.getLogger(__name__)
MY_CONFIG_NAME = 'i3configger.json'
STATE_FILE_NAME = '.state.json'
MY_CONFIG_FOLDER = 'config.d'
MY_REL_CONFIG_PATH = MY_CONFIG_FOLDER + '/' + MY_CONFIG_NAME
STATE_CONFIG_PATH = MY_CONFIG_FOLDER + '/' + STATE_FILE_NAME


def get_my_config_path(configPath=None):
    if not configPath:
        i3configPath = get_i3_config_path()
        configContainer = i3configPath / MY_CONFIG_FOLDER
        if not configContainer.exists():
            log.info("create new config folder at %s", configContainer)
            configContainer.mkdir()
        configPath = configContainer / MY_CONFIG_NAME
    elif configPath.is_dir():
            configPath /= MY_CONFIG_NAME
    if not configPath.exists():
        log.info("create default configuration at %s", configPath)
        myConfigBlueprint = Path(__file__).parent / MY_CONFIG_NAME
        with open(myConfigBlueprint) as f:
            I3configgerConfig.freeze(configPath, json.load(f))
    return configPath


def get_i3_config_path():
    """Use same search order like i3 (no system stuff though).

    see: https://github.com/i3/i3/blob/4.13/libi3/get_config_path.c#L31
    """
    candidates = [
        Path('~/.i3').expanduser(),
        Path(os.getenv("XDG_CONFIG_HOME", '~/.config/')).expanduser() / 'i3']
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise exc.ConfigError(
        f"can't find i3 config at the standard locations: {candidates}")


class I3configgerConfig:
    def __init__(self, configPath, message: list=None, freeze=True):
        # TODO checks with helpful errors for screwed up configurations
        path = Path(configPath)
        assert path.exists() and path.is_file(), path
        self.configPath = path
        self.partialsPath = path.parent.resolve()
        self.payload = self.read(self.configPath)
        main = self.payload["main"]
        targetPath = Path(main["target"]).expanduser()
        if targetPath.is_absolute():
            self.mainTargetPath = targetPath.resolve()
        else:
            self.mainTargetPath = (self.partialsPath / targetPath).resolve()
        bars = self.payload.get("bars", {})
        self.bars = self.resolve(bars)
        log.debug("initialized config  %s", self)
        state = self.payload.get("state", {})
        self.select = state.get(Message.SELECT[0], {})
        self.set = state.get(Message.SET[0], {})
        if message:
            # TODO send message to .state.json instead
            Message.process(message, self)
            if freeze:
                log.info("freezing config to %s", self.configPath)
                self._freeze()

    def __str__(self):
        return "%s:\n%s" % (self.__class__.__name__,
                            pprint.pformat(vars(self)))

    def resolve(self, bars):
        defaults = bars.get("defaults", {})
        del bars["defaults"]
        resolvedBars = {}
        for name, bar in bars.items():
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
            log.debug("use:\n%s", pprint.pformat(payload))
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
    _ALL = [SELECT_NEXT, SELECT_PREVIOUS, SELECT, SET]
    DEL = 'del'

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
        raise exc.MessageError(f"unknown message: {message}. "
                               f"I only now: {[m[0] for m in cls._ALL]}")

    @classmethod
    def process(cls, message: list, cnf: I3configgerConfig):
        # todo manipulate a .state.json and override values from conf instead
        command, key, *rest = message
        value = rest[0] if rest else None
        log.debug(f"sending message {message} to {cnf}")
        if command == cls.SET:
            if value.lower() == cls.DEL:
                del cnf.set[key]
            else:
                cnf.set[key] = value
        else:
            prts = partials.create(cnf.partialsPath)
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
                if value.lower == cls.DEL:
                    del cnf.select[key]
                else:
                    cnf.select[key] = candidate.value
