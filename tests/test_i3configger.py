import os
from pathlib import Path

import pytest as pytest

from i3configger.lib import I3Configger


class ConfDouble:
    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            return None


@pytest.fixture
def tmpdir(tmpdir):
    return Path(tmpdir)


@pytest.fixture(name="miniConf")
def cnf(tmpdir):
    filler = ConfDouble()
    sources = tmpdir / 'sources'
    filler.sources = str(sources)
    filler.destination = str(tmpdir / 'config')
    os.mkdir(filler.sources)
    testfile = sources / 'testfile'
    testfile.write_text("some text in some file")
    return filler


def test_irconfigger(miniConf):
    i3configger = I3Configger(miniConf)
    assert i3configger.tree
