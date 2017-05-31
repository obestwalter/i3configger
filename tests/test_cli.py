import pytest

from i3configger import cli, exc


@pytest.mark.parametrize(
    "args,exp",
    (
        ([], True),
        ([''], False),
        (['dunno'], False),
        (['next'], False),
        (['previous'], False),
        (['set'], False),
        (['select'], False),
        # TODO do I want special stuff to be overridable?
        (['select', 'hostname', 'ob1'], True),
        (['set', 'someVar', 'someValue'], True),
        (['set', 'someVar'], False),
        (['next', 'scheme'], True),
        (['next', 'scheme', 'extra'], False),
        (['previous', 'scheme'], True),
        (['previous', 'scheme', 'extra'], False),
    )
)
def test_check_sanity(args, exp):
    if exp:
        cli.check_sanity(args)
    else:
        with pytest.raises(exc.I3configgerException):
            cli.check_sanity(args)
