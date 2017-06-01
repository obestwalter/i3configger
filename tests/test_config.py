import json
from pathlib import Path

from i3configger import config


def test_no_config(tmpdir, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    monkeypatch.setattr(config, 'get_i3_config_path', lambda: Path(tmpdir))
    path = config.get_my_config_path()
    assert path.exists()
    assert path.is_file()
    assert path.name == config.MY_CONFIG_NAME
    payload = json.loads(path.read_text())
    assert 'main' in payload
    assert 'bars' in payload
    assert 'message' in payload
