import logging
import os
import shutil
from pathlib import Path

from i3configger import config, exc

log = logging.getLogger(__name__)

I3CONFIGGER_CONFIG_NAME = 'i3configger.json'
MESSAGES_NAME = '.messages.json'
PARTIALS_NAME = 'config.d'


class Paths:
    def __init__(self, configPath):
        path = Path(configPath)
        assert path.exists() and path.is_file(), path
        self.root = path.parent
        self.config = configPath
        self.messages = self.root / MESSAGES_NAME


def ensure_i3_configger_sanity(configPath=None) -> Path:
    i3wmConfigPath = get_i3wm_config_path()
    partialsPath = i3wmConfigPath / PARTIALS_NAME
    if not partialsPath.exists():
        log.info("create new config folder at %s", partialsPath)
        partialsPath.mkdir()
        for candidate in [i3wmConfigPath / 'config', Path('etc/i3/config')]:
            if candidate.exists():
                log.info("populate config with %s", candidate)
                shutil.copy2(candidate, partialsPath / 'config.conf')
    if not configPath:
        configPath = partialsPath / I3CONFIGGER_CONFIG_NAME
    elif configPath.is_dir():
            configPath /= I3CONFIGGER_CONFIG_NAME
    if not configPath.exists():
        log.info("create default configuration at %s", configPath)
        config.freeze(configPath, config.I3_CONFIGGER_DEFAULTS)
    return configPath


def get_i3wm_config_path():
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
