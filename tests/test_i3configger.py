import os
from configparser import ConfigParser
from pathlib import Path

import pytest as pytest
from inotify.adapters import Inotify

from i3configger.lib import I3Configger, IniConfig


class ConfDouble:
    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            return None


# noinspection PyShadowingNames
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


def test_default_config_sanity():
    """rudimentary check of the default ini file"""
    cp = Path(__file__).parents[1] / 'i3configger' / 'i3configger.ini'
    assert cp.exists()
    config = ConfigParser()
    config.read(cp)
    assert '.log' in config['settings']['logfile']
    assert 'builddef:i3config' in config.sections()
    assert 'target' in config['builddef:i3config']


def test_settings():
    wanted = Path('~/.i3/i3configger.log').expanduser()
    config = IniConfig(IniConfig.get_config())
    assert config.logfile == wanted


def test_build_defs():
    cnf = IniConfig(IniConfig.get_config())
    df = cnf.buildDefs[0]
    assert df.sources == [Path('~/.i3/config.d').expanduser()]
    assert isinstance(df.theme, str)


def test_i3configger(miniConf):
    config = IniConfig(IniConfig.get_config())
    i3configger = I3Configger(config.buildDefs, config.suffix)
    assert isinstance(i3configger.inotify_watcher, Inotify)
    i3configger.build()
