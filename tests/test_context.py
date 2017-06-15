import pytest as pytest

from i3configger import context, exc

verySimple = {"$k1": "v1", "$k2": "v2"}
simple = {"$k1": "v1", "$k2": "v1"}
undef = {"$k1": "v1", "$k2": "$undef"}
oneIndirection = {"$k1": "$k2", "$k2": "v1"}
twoIndirections = {"$k1": "$k2", "$k2": "$k3", "$k3": "v1"}
unresolvedIndirection = {"$k1": "$k2", "$k2": "$k3", "$k3": "$k4"}


@pytest.mark.parametrize(
    "ctx, exp",
    (
        (verySimple, verySimple),
        (simple, {"$k1": "v1", "$k2": "v1"}),
        (undef, exc.ContextError),
        (oneIndirection, {"$k1": "v1", "$k2": "v1"}),
        (twoIndirections, {"$k1": "v1", "$k2": "v1", "$k3": "v1"}),
        (unresolvedIndirection, exc.ContextError),
    )
)
def test_context(ctx, exp):
    if isinstance(exp, dict):
        ctx = context.resolve_variables(ctx)
        assert ctx == exp
    else:
        with pytest.raises(exc.ContextError):
            context.resolve_variables(ctx)
