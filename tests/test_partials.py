from pathlib import Path

import pytest

from i3configger import exc, partials

DATA = Path(__file__).parents[1] / 'examples'


def test_create():
    path = DATA / 'selectors' / 'config.d'
    prts = partials.create(path)
    assert len(prts) == 4


@pytest.mark.parametrize(
    "key, value, exp", (
        ('', '', exc.ConfigError),
        ('some-key', '', exc.ConfigError),
        ('', '', exc.ConfigError),
        (None, None, exc.ConfigError),
        ('non-existing-key', 'some-value', exc.ConfigError),
        ('non-existing-key', 'none-existing-value', exc.ConfigError),
        ('some-key', 'none-existing-value', exc.ConfigError),
        ('some-key', 'some-value', True),
        ('other-key', 'other-value', True),
    )
)
def test_select_non_existing(key, value, exp):
    path = DATA / 'selectors' / 'config.d'
    prts = partials.create(path)
    selector = {key: value}
    if not isinstance(exp, bool):
        with pytest.raises(exp):
            partials.select(prts, selector)
    else:
        selected = partials.select(prts, selector)
        found = partials.find(prts, key, value)
        assert selected[1].name == 'unconditional'
        assert isinstance(selected[0], partials.Partial)
        assert isinstance(found, partials.Partial)
        assert selected[0] == found
        assert selected[0].key == key
        assert selected[0].value == value
