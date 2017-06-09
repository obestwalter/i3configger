import os
import shutil
from pathlib import Path

import pytest

from i3configger import build, paths, message, partials

HERE = Path(__file__).parent
EXAMPLES = HERE.parent / 'examples'
REFERENCE = HERE / 'examples'
FAKE_HEADER = """\
###############################################################################
# Built by i3configger /from/some/directory/who/cares  (some time after 1972) #
###############################################################################
"""
TEST_FOLDER_NAMES = sorted(list(
    [d.name for d in EXAMPLES.iterdir()
     if d.is_dir() and not str(d.name).startswith('_')]))


@pytest.mark.parametrize("container", TEST_FOLDER_NAMES)
def test_build(container, monkeypatch):
    monkeypatch.setattr(
        paths, 'get_i3_config_path', lambda: EXAMPLES / container)
    monkeypatch.setattr(build, 'make_header', lambda _: FAKE_HEADER)
    if not shutil.which('i3'):
        # we're on CI
        monkeypatch.setattr(build, 'check_config', lambda _: True)
    configPath = paths.get_my_config_path()
    assert configPath.exists() and configPath.is_file()
    p = paths.Paths(configPath)
    prts = partials.create(p.root)
    message.Messenger(p.messages, prts)
    try:
        build.build_all(configPath)
        buildPath = configPath.parents[1]
        referencePath = REFERENCE / container
        names = [p.name for p in referencePath.iterdir()]
        assert names
        for name in names:
            resultFilePath = buildPath / name
            referenceFilePath = (referencePath / name)
            assert resultFilePath != referenceFilePath
            result = resultFilePath.read_text()
            reference = referenceFilePath.read_text()
            assert result == reference
    finally:
        if p.messages.exists():
            os.unlink(p.messages)
