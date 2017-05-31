import json
from pathlib import Path

import pytest

from i3configger import config

HERE = Path(__file__).parent
SOURCES = HERE / 'fake_sources'
TARGET = HERE / 'fake_target'


def test_no_config(tmpdir):
    """Given empty sources directory a new config is created from defaults"""
    cnf = config.read_config(tmpdir)
    with open(Path(config.__file__).parent / config.NAME) as f:
        assert cnf == json.load(f)
