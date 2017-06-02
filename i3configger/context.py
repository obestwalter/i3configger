import logging
import typing as t

from i3configger import base, exc, partials

log = logging.getLogger(__name__)


def create(prts: t.Iterable[partials.Partial]) -> dict:
    """Read variables from all partials into a dictionary and resolve them."""
    ctx = {}
    for context in [fetch(p.payload) for p in prts]:
        ctx.update(context)
    ctx = resolve(ctx)
    assert all(k.startswith(base.VAR_MARK) for k in ctx.keys()), ctx
    ctx = remove_variable_markers(ctx)
    assert not any(k.startswith(base.VAR_MARK) for k in ctx.keys()), ctx
    assert not any(v.startswith(base.VAR_MARK) for v in ctx.values()), ctx
    return ctx


def remove_variable_markers(ctx: dict) -> dict:
    cleaned = {}
    lvm = len(base.VAR_MARK)
    for key, value in ctx.items():
        key = key[lvm:] if key.startswith(base.VAR_MARK) else key
        cleaned[key] = value
    return cleaned


def enhance(ctx, otherContexts):
    eCtx = dict(ctx)
    for oc in otherContexts:
        if isinstance(oc, partials.Partial):
            oc = create([oc])
        eCtx.update(oc)
    return eCtx


def resolve(context: dict) -> dict:
    """If variables are set by a variable, replace them by their value."""
    if not any(v.startswith(base.VAR_MARK) for v in context.values()):
        log.debug("needs no resolution: %s", context)
        return context
    resolvedContext = {}
    seenKeys = []
    for key, value in context.items():
        if key in seenKeys:
            raise exc.DuplicateKey("%s -> %s would be overridden with %s",
                                   key, context[key], value)
        if value.startswith(base.VAR_MARK):
            try:
                resolvedContext[key] = context[value]
            except KeyError:
                log.exception("[IGNORED] %s, %s", key, value)
        else:
            resolvedContext[key] = value
    return resolvedContext


def fetch(content: str) -> dict:
    ctx = {}
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith(base.SET_MARK):
            continue
        payload = line.split(maxsplit=1)[1]
        key, value = payload.split(maxsplit=1)
        ctx[key] = value
    return ctx
