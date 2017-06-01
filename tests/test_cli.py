import pytest

from i3configger import cli, exc


@pytest.mark.parametrize(
    "args,exp",
    (
        ([], True),
        ([''], False),
        (['dunno'], False),
        (['select-next'], False),
        (['select-previous'], False),
        (['set'], False),
        (['select'], False),
        # TODO do I want special stuff to be overridable?
        (['select', 'hostname', 'ob1'], True),
        (['set', 'someVar', 'someValue'], True),
        (['set', 'someVar'], False),
        (['select-next', 'scheme'], True),
        (['select-next', 'scheme', 'extra'], False),
        (['select-previous', 'scheme'], True),
        (['select-previous', 'scheme', 'extra'], False),
    )
)
def test_check_sanity(args, exp):
    if exp:
        cli.check_sanity(args)
    else:
        with pytest.raises(exc.I3configgerException):
            cli.check_sanity(args)
