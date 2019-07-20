"""i3configger configuration functionality."""
import copy
import json
import logging
import os
import pprint
import shutil
from pathlib import Path

from i3configger import context, exc

log = logging.getLogger(__name__)
cliMainOverrideMap: dict = {}
"""holds parsed args if started from cli and was initialized"""


class MARK:
    COMMENT = "#"
    SET = "set"
    VAR = "$"


SUFFIX = ".conf"
I3BAR = "i3bar"
"""reserved key for status bar template files"""


DEFAULTS = {
    "main": {
        "target": "../config",
        "i3_refresh_msg": "reload",
        "status_command": "i3status",
        "log": None,
        "notify": False,
    },
    "bars": {
        "defaults": {"template": "tpl", "target": "..", "select": "default"},
        "targets": {},
    },
}
CONFIG_CANDIDATES = [
    Path("~/.i3").expanduser(),
    Path(os.getenv("XDG_CONFIG_HOME", "~/.config/")).expanduser() / "i3",
]


class I3configgerConfig:
    PARTIALS_NAME = "config.d"
    CONFIG_NAME = "i3configger.json"
    MESSAGES_NAME = ".messages.json"

    def __init__(self, load=True):
        i3configBasePath = get_i3wm_config_path()
        self.partialsPath = i3configBasePath / self.PARTIALS_NAME
        self.configPath = self.partialsPath / self.CONFIG_NAME
        self.messagesPath = self.partialsPath / self.MESSAGES_NAME
        if load:
            self.load()

    def __str__(self):
        return f"{self.__class__.__name__}:\n{pprint.pformat(vars(self))}"

    def load(self):
        """Layered overrides `DEFAULTS` -> `i3configger.json`-> `args`"""
        cnfFromDefaults = copy.deepcopy(DEFAULTS)
        cnfFromFile = fetch(self.configPath)
        self.payload = context.merge(cnfFromDefaults, cnfFromFile)
        mainOverrides = dict(main=cliMainOverrideMap)
        self.payload = context.merge(self.payload, mainOverrides)
        targetPath = Path(self.payload["main"]["target"]).expanduser()
        if targetPath.is_absolute():
            self.targetPath = targetPath.resolve()
        else:
            self.targetPath = (self.partialsPath / targetPath).resolve()

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


def fetch(path: Path) -> dict:
    if not path.exists():
        raise exc.ConfigError(f"config not found at {path}")
    payload = json.loads(path.read_text())
    log.debug(f"{path}:\n{pprint.pformat(payload)}")
    return payload


def freeze(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True, indent=2))
    log.debug(f"froze {pprint.pformat(obj)} to {path}")


def ensure_i3_configger_sanity():
    i3wmConfigPath = get_i3wm_config_path()
    partialsPath = i3wmConfigPath / I3configgerConfig.PARTIALS_NAME
    if not partialsPath.exists():
        log.info(f"create new config folder at {partialsPath}")
        partialsPath.mkdir()
        for candidate in [i3wmConfigPath / "config", Path("etc/i3/config")]:
            if candidate.exists():
                log.info(f"populate config with {candidate}")
                shutil.copy2(candidate, partialsPath / "config.conf")
    configPath = partialsPath / I3configgerConfig.CONFIG_NAME
    if not configPath.exists():
        log.info(f"create default configuration at {configPath}")
        freeze(configPath, DEFAULTS)


def get_i3wm_config_path():
    """Use same search order like i3 (no system stuff though).

    see: https://github.com/i3/i3/blob/4.13/libi3/get_config_path.c#L31
    """
    for candidate in CONFIG_CANDIDATES:
        if candidate.exists():
            return candidate
    raise exc.ConfigError(
        f"can't find i3 config at the standard locations: {CONFIG_CANDIDATES}"
    )
