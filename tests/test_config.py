import json
from pathlib import Path

import i3configger.paths
from i3configger import paths


def test_no_config(tmpdir, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    monkeypatch.setattr(paths, 'get_i3_config_path', lambda: Path(tmpdir))
    path = i3configger.paths.get_my_config_path()
    assert path.exists()
    assert path.is_file()
    assert path.name == i3configger.paths.MY_CONFIG_NAME
    payload = json.loads(path.read_text())
    assert 'main' in payload
    assert 'bars' in payload
    assert 'targets' in payload['bars']
