import json
import logging
import pprint
from pathlib import Path

from i3configger import base, exc

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
    def __init__(self, configPath: Path):
        p = base.Paths(configPath)
        self.configPath = configPath
        self.partialsPath = p.root
        self.payload = fetch(self.configPath)
        targetPath = Path(self.payload["main"]["target"]).expanduser()
        if targetPath.is_absolute():
            self.mainTargetPath = targetPath.resolve()
        else:
            self.mainTargetPath = (self.partialsPath / targetPath).resolve()

    def __str__(self):
        return "%s:\n%s" % (self.__class__.__name__,
                            pprint.pformat(vars(self)))

    def get_bar_targets(self):
        """Create a resolved copy of the bar settings."""
        barTargets = {}
        barSettings = self.payload.get("bars", {})
        if not barSettings:
            return barTargets
        defaults = barSettings.get("defaults", {})
        for name, bar in barSettings["targets"].items():
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
        raise exc.ConfigError(f"file not found: {path}")
    with path.open() as f:
        log.info(f"fetch from {path}")
        payload = json.load(f)
        log.debug(f"{path}: {pprint.pformat(payload)}")
        return payload


def freeze(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=2)
    log.debug("froze %s to %s", pprint.pformat(obj), path)
