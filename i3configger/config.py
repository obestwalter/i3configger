import json
import logging
import pprint
from pathlib import Path

from i3configger import exc, partials, paths

log = logging.getLogger(__name__)

I3_CONFIGGER_DEFAULTS = {
  "main": {
    "target": "../config",
  },
  "bars": {
    "defaults": {
      "target": "..",
      "template": "tpl",
      "key": "i3status",
      "value": "default"
    },
    "targets": {}
  }
}


class I3configgerConfig:
    def __init__(self, configPath: Path, message: list=None):
        # TODO checks with helpful errors for screwed up configurations
        self.message = message
        p = paths.Paths(configPath)
        self.configPath = p.config
        self.partialsPath = p.root
        self.statePath = p.state
        self.payload = fetch(self.configPath)
        self.state = State.process(
            self.statePath, partials.create(self.partialsPath), self.message)
        targetPath = Path(self.payload["main"]["target"]).expanduser()
        if targetPath.is_absolute():
            self.mainTargetPath = targetPath.resolve()
        else:
            self.mainTargetPath = (self.partialsPath / targetPath).resolve()
        self.barTargets = self.make_bar_targets(self.payload.get("bars", {}))
        log.debug("initialized config  %s", self)

    def __str__(self):
        return "%s:\n%s" % (self.__class__.__name__,
                            pprint.pformat(vars(self)))

    def make_bar_targets(self, bars):
        """Create a resolved copy of the bar settings."""
        barTargets = {}
        if not bars:
            return barTargets
        defaults = bars.get("defaults", {})
        for name, bar in bars["targets"].items():
            newBar = dict(bar)
            barTargets[name] = newBar
            for defaultKey, defaultValue in defaults.items():
                if defaultKey not in newBar:
                    newBar[defaultKey] = defaultValue
        return barTargets


class State:
    """Process a message to alter the configuration to be build.

    Tuple contains name and number of expected additional arguments
    """
    I3STATUS = "i3status"
    """reserved key for status bar setting files"""
    SELECT_NEXT = ("select-next", 1)
    SELECT_PREVIOUS = ("select-previous", 1)
    SELECT = ("select", 2)
    SET = ("set", 2)
    _ALL = [SELECT_NEXT, SELECT_PREVIOUS, SELECT, SET]
    DEL = 'del'

    @classmethod
    def process(cls, statePath, prts, message):
        state = cls.fetch_state(statePath, prts)
        if not message:
            return state
        command, key, *rest = message
        value = rest[0] if rest else None
        log.debug(f"sending message {message} to {statePath}")
        if command == cls.SET[0]:
            if value.lower() == cls.DEL:
                del state["set"][key]
            else:
                state["set"][key] = value
        else:
            if command in [cls.SELECT_NEXT[0], cls.SELECT_PREVIOUS[0]]:
                candidates = partials.find(prts, key)
                if not candidates:
                    raise exc.MessageError(
                        f"No candidates for {message} in {prts}")
                if command == cls.SELECT_PREVIOUS[0]:
                    candidates = reversed(candidates)
                current = state["select"].get(key) or candidates[0].key
                for idx, candidate in enumerate(candidates):
                    if candidate.value == current:
                        try:
                            new = candidates[idx + 1]
                        except IndexError:
                            new = candidates[0]
                        log.info("select %s.%s", key, new)
                        state["select"][key] = new.value
                        break
            elif command == cls.SELECT[0]:
                candidate = partials.find(prts, key, value)
                if not candidate:
                    raise exc.MessageError(f"No candidate for {message}")
                if value.lower == cls.DEL:
                    del state["select"][key]
                else:
                    state["select"][key] = candidate.value
        freeze(statePath, state)
        return state

    @classmethod
    def fetch_state(cls, statePath, prts):
        if not statePath.exists():
            return cls.populate_initial_state(statePath, prts)
        return fetch(statePath)

    @classmethod
    def populate_initial_state(cls, statePath, prts):
        """fetch first of each selectable partials to have a sane state"""
        selects = {}
        for prt in prts:
            if not prt.needsSelection:
                continue
            if prt.key not in selects and prt.key != cls.I3STATUS:
                selects[prt.key] = prt.value
        state = dict(select=selects, set={})
        freeze(statePath, state)
        return state

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
        json.dump(obj, f, sort_keys=True, indent=2)
    log.debug("froze %s to %s", pprint.pformat(obj), path)
