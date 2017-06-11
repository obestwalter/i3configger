from pathlib import Path

import pytest

from i3configger import exc, partials

SCHEMES = Path(__file__).parents[1] / 'examples' / '4-schemes' / 'config.d'


def test_create():
    prts = partials.create(SCHEMES)
    assert len(prts) == 3


@pytest.mark.parametrize(
    "key, value, exp", (
        ('', '', exc.ConfigError),
        ('some-key', '', exc.ConfigError),
        ('', '', exc.ConfigError),
        (None, None, exc.ConfigError),
        ('non-existing-key', 'some-value', exc.ConfigError),
        ('non-existing-key', 'none-existing-value', exc.ConfigError),
        ('some-category', 'none-existing-value', exc.ConfigError),
        ('some-key', 'value1', True),
        ('some-key', 'value2', True),
    )
)
def test_select(key, value, exp):
    prts = partials.create(SCHEMES)
    selector = {key: value}
    if not isinstance(exp, bool):
        with pytest.raises(exp):
            partials.select(prts, selector)
    else:
        selected = partials.select(prts, selector)
        found = partials.find(prts, key, value)
        assert all(isinstance(p, partials.Partial) for p in selected)
        assert selected[0] == found
        assert selected[0].key == key
        assert selected[0].value == value
