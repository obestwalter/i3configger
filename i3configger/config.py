import json
import logging
import pprint
from pathlib import Path

from i3configger import exc, partials, paths

log = logging.getLogger(__name__)


class I3configgerConfig:
    def __init__(self, configPath: Path, message: list=None):
        # TODO checks with helpful errors for screwed up configurations
        p = paths.Paths(configPath)
        self.configPath = p.config
        self.partialsPath = p.root
        self.prts = partials.create(self.partialsPath)
        self.statePath = p.state
        self.payload = fetch(self.configPath)
        targetPath = Path(self.payload["main"]["target"]).expanduser()
        if targetPath.is_absolute():
            self.mainTargetPath = targetPath.resolve()
        else:
            self.mainTargetPath = (self.partialsPath / targetPath).resolve()
        self.bars = self.populate_bar_defaults(self.payload.get("bars", {}))
        self.state = State.process(self.statePath, message)
        log.debug("initialized config  %s", self)

    def __str__(self):
        return "%s:\n%s" % (self.__class__.__name__,
                            pprint.pformat(vars(self)))

    def populate_bar_defaults(self, bars):
        """Create a resolved copy of the bar settings."""
        defaults = bars.get("defaults", {})
        resolvedBars = {}
        for name, bar in bars.items():
            if name == "defaults":
                continue
            newBar = dict(bar)
            resolvedBars[name] = newBar
            for defaultKey, defaultValue in defaults.items():
                if defaultKey not in newBar:
                    newBar[defaultKey] = defaultValue
        return resolvedBars


class State:
    """Process a message to alter the configuration to be build.

    Tuple contains name and number of expected additional arguments
    """
    SELECT_NEXT = ("select-next", 1)
    SELECT_PREVIOUS = ("select-previous", 1)
    SELECT = ("select", 2)
    SET = ("set", 2)
    _ALL = [SELECT_NEXT, SELECT_PREVIOUS, SELECT, SET]
    DEL = 'del'

    @classmethod
    def process(cls, statePath, prts, message):
        state = fetch(statePath)
        command, key, *rest = message
        value = rest[0] if rest else None
        log.debug(f"sending message {message} to {statePath}")
        if command == cls.SET:
            if value.lower() == cls.DEL:
                del state["set"][key]
            else:
                state["set"][key] = value
        else:
            if command in [cls.SELECT_NEXT, cls.SELECT_PREVIOUS]:
                candidates = partials.find(prts, key)
                if not candidates:
                    raise exc.MessageError(
                        f"No candidates for {message} in {prts}")
                current = state["select"].get(key) or candidates[-1]
                new = cls.FUNC_MAP[command](current, candidates)
                state["select"][key] = new.value
            elif command == cls.SELECT:
                candidate = partials.find(prts, key, value)
                if not candidate:
                    raise exc.MessageError(f"No candidate for {message}")
                if value.lower == cls.DEL:
                    del state["select"][key]
                else:
                    state["select"][key] = candidate.value
        freeze(statePath, state)

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


def fetch(path):
    if not path.exists():
        raise exc.ConfigError(f"No config found at {path}")
    with path.open() as f:
        log.info("read config from %s", path)
        payload = json.load(f)
        log.debug("use:\n%s", pprint.pformat(payload))
        return payload


def freeze(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=4)
    log.debug("froze %s to %s", pprint.pformat(obj), path)
