from pathlib import Path

import pytest

from i3configger import build, paths

HERE = Path(__file__).parent
EXAMPLES = HERE.parent / 'examples'


@pytest.mark.parametrize(
    "container", (
        "default", "selectors"
    ))
def test_no_config(container, monkeypatch):
    """Given empty sources directory a new config is created from defaults"""
    pytest.skip("WIP")
    container = EXAMPLES / container
    monkeypatch.setattr(paths, 'get_i3_config_path', lambda: container)
    configPath = paths.get_my_config_path()
    assert configPath.exists() and configPath.is_file()

    builder = build.Builder(configPath)
    builder.build()
    assert 0
