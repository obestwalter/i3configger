from pathlib import Path

from i3configger.base import I3Status

DATA = Path(__file__).parent / 'data'


def test_no_file():
    I3Status.FILE_NAME = 'i-do-not-exist'
    i3s = I3Status(DATA)
    assert not i3s
    assert not hasattr(i3s, 'bars')
    assert not hasattr(i3s, 'defaults')


def test_empty_file():
    I3Status.FILE_NAME = 'i3status-empty.json'
    i3s = I3Status(DATA)
    assert not i3s
    assert not hasattr(i3s, 'bars')
    assert not hasattr(i3s, 'defaults')


def test_only_bars():
    I3Status.FILE_NAME = 'i3status-only-bars.json'
    i3s = I3Status(DATA)
    assert i3s
    assert i3s.bars == {"laptop": {"output": "DP-3", "position": "top"}}
    assert i3s.marker == I3Status.DEFAULT_SETTINGS[i3s.MARKER]
    assert i3s.template == I3Status.DEFAULT_SETTINGS[i3s.TEMPLATE]
    assert i3s.target == I3Status.DEFAULT_SETTINGS[i3s.TARGET]
    assert i3s.defaults == {}


def test_full():
    I3Status.FILE_NAME = 'i3status-full.json'
    i3s = I3Status(DATA)
    assert i3s
    assert i3s.bars == {
        'first bar': {
            'font': 'should override font default',
            'output': 'first output',
            'source': 'some default source'},
        'second bar': {
            'font': 'some default font',
            'output': 'second output',
            'source': 'should override source default'}}
    assert i3s.marker == "not marker default"
    assert i3s.template == "not template default"
    assert i3s.target == i3s.DEFAULT_SETTINGS[i3s.TARGET]
    assert i3s.defaults == {"font": "some default font",
                            "source": "some default source"}
