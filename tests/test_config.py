import json
from pathlib import Path

import i3configger.paths
from i3configger import paths


def test_no_config(tmpdir, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    tmpdir = Path(tmpdir)
    monkeypatch.setattr(paths, 'get_i3wm_config_path', lambda: tmpdir)
    assert not (tmpdir / 'config.d').exists()
    path = i3configger.paths.ensure_i3_configger_sanity()
    assert path.exists()
    assert path.is_file()
    assert path.name == i3configger.paths.I3CONFIGGER_CONFIG_NAME
    payload = json.loads(path.read_text())
    assert 'main' in payload
    assert 'bars' in payload
    assert 'targets' in payload['bars']
    assert 'set' not in payload
    assert 'select' not in payload
    assert 'shadow' not in payload
