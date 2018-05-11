import json

import pytest

from i3configger import config


def test_initialization(tmpdir, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    monkeypatch.setattr(config, 'get_i3wm_config_path', lambda: tmpdir)
    assert not (tmpdir / 'config.d').exists()
    config.ensure_i3_configger_sanity()
    cnf = config.I3configgerConfig()
    assert cnf.configPath.exists()
    assert cnf.configPath.is_file()
    assert cnf.configPath.name == config.I3configgerConfig.CONFIG_NAME
    payload = json.loads(cnf.configPath.read_text())
    assert 'main' in payload
    assert 'bars' in payload
    assert 'targets' in payload['bars']
    assert 'set' not in payload
    assert 'select' not in payload
    assert 'shadow' not in payload


@pytest.mark.xfail(reason="test if already implemented, or implement it")
def test_config_backup_is_not_overwritten():
    """Going through the docs I saw this:

    WARNING going ahead will overwrite your existing config file, so make
    sure your config is under source control and/or you have a backup.
    i3configger will create a backup of your old config but only one,
    so running i3configger twice will leave no trace of your original
    configuration file.

    http://oliver.bestwalter.de/i3configger/getting-started/

    I though I fixed that, but am not sure so this test should make sure that
    the original config backup gets never overwritten.
    """
    assert 0  # FIXME
