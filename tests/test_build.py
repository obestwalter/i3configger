from pathlib import Path

import pytest
from pytest import fixture

from i3configger.configger import I3Configger, MalformedAssignment


# noinspection PyShadowingNames
@fixture
def tmpdir(tmpdir):
    return Path(tmpdir)


@pytest.mark.parametrize(
    "line, exp",
    (
        ("set $var value", ("$var", "value")),
        (" set $var value", ("$var", "value")),
        (" set   $var #FFFFFF", ("$var", "#FFFFFF")),
        (" set   $var #FFFFFF # comment", ("$var", "#FFFFFF")),
        (" set   $var value # some comment", ("$var", "value")),
        ("set $var value other value  # comment ###",
         ("$var", "value other value")),
        ("set $var $otherVar  $otheVar", ("$var", "$otherVar  $otheVar")),
        (" set   $var #FFFFFF #malformed comment", MalformedAssignment),
        ("set spam eggs spam", MalformedAssignment),
        ("set", MalformedAssignment),
        ("set $var", MalformedAssignment),
    )
)
def test_get_assignment(line, exp):
    if not isinstance(exp, tuple):
        with pytest.raises(MalformedAssignment):
            I3Configger.get_assignment(line)
    else:
        assert I3Configger.get_assignment(line) == exp
