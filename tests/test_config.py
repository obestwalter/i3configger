import json

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
