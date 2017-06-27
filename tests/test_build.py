from pathlib import Path

import pytest

from i3configger import build, config

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
@pytest.mark.usefixtures('deactivate_ipc')
def test_build(container, monkeypatch):
    monkeypatch.setattr(
        config, 'get_i3wm_config_path', lambda: EXAMPLES / container)
    monkeypatch.setattr(build, 'make_header', lambda _: FAKE_HEADER)
    monkeypatch.setattr(build, 'check_config', lambda _: True)
    config.ensure_i3_configger_sanity()
    cnf = config.I3configgerConfig()
    assert cnf.configPath.exists() and cnf.configPath.is_file()
    build.build_all()
    buildPath = cnf.configPath.parents[1]
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
