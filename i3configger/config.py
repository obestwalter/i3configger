import json
import logging
import pprint
from pathlib import Path

from i3configger import exc, paths

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
        self.message = message
        self.statePath = p.state
        self.payload = fetch(self.configPath)
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
            container = Path(newBar["target"])
            if not container.is_absolute():
                container = (self.partialsPath / container).resolve()
            newBar["target"] = str(container)
        return barTargets


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
