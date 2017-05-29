from pathlib import Path

from i3configger.base import I3Status

DATA = Path(__file__).parent / 'data'


def test_no_file():
    I3Status.FILE_NAME = 'i-do-not-exist'
    i3s = I3Status(DATA)
    assert not hasattr(i3s, 'bars')
    assert not hasattr(i3s, 'settings')
    assert not hasattr(i3s, 'defaults')


def test_empty_file():
    I3Status.FILE_NAME = 'i3status-empty.json'
    i3s = I3Status(DATA)
    assert not hasattr(i3s, 'bars')
    assert not hasattr(i3s, 'settings')
    assert not hasattr(i3s, 'defaults')


def test_only_bars():
    I3Status.FILE_NAME = 'i3status-only-bars.json'
    i3s = I3Status(DATA)
    assert i3s.bars == {"laptop": {"output": "DP-3", "position": "top"}}
    assert i3s.settings == I3Status.DEFAULT_SETTINGS
    assert i3s.defaults == {}


def test_full():
    I3Status.FILE_NAME = 'i3status-full.json'
    i3s = I3Status(DATA)
    assert i3s.bars == {
        'first bar': {
            'font': 'should override font default',
            'output': 'first output',
            'source': 'some default source'},
        'second bar': {
            'font': 'some default font',
            'output': 'second output',
            'source': 'should override source default'}}
    assert i3s.settings["marker"] == "not marker default"
    assert i3s.settings["template"] == "not template default"
    assert i3s.settings["target"] == i3s.DEFAULT_SETTINGS[i3s.TARGET]
    assert i3s.defaults == {"font": "some default font",
                            "source": "some default source"}
