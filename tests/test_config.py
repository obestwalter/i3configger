import json
from pathlib import Path

from i3configger import config
from i3configger.build import persist_results


def test_initialization(tmp_path, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    monkeypatch.setattr(config, "get_i3wm_config_path", lambda: tmp_path)
    assert not (tmp_path / "config.d").exists()
    config.ensure_i3_configger_sanity()
    cnf = config.I3configgerConfig()
    assert cnf.configPath.exists()
    assert cnf.configPath.is_file()
    assert cnf.configPath.name == config.I3configgerConfig.CONFIG_NAME
    payload = json.loads(cnf.configPath.read_text())
    assert "main" in payload
    assert "bars" in payload
    assert "targets" in payload["bars"]
    assert "set" not in payload
    assert "select" not in payload
    assert "shadow" not in payload


def test_config_backup_is_not_overwritten(tmp_path):
    """Given an existing backup it is not overwritten by subsequent builds."""
    firstThing = "first thing"
    somePath = tmp_path / "some-path.txt"
    backupPath = Path(str(somePath) + ".bak")
    somePath.write_text(firstThing)
    persist_results({somePath: firstThing})
    assert backupPath.read_text() == firstThing
    otherThing = "other thing"
    persist_results({somePath: otherThing})
    assert somePath.read_text() == otherThing
    assert backupPath.read_text() == firstThing
