import collections
import logging
import typing as t

from i3configger import base, exc, partials

log = logging.getLogger(__name__)
SET_MARK = 'set'
SETTINGS_MARK = base.VAR_MARK + SET_MARK + '_'


def create(prts: t.List[partials.Partial]) -> t.Tuple[dict, dict]:
    """Read variables from all partials into a dictionary and resolve them."""
    ctx = {}
    for context in [fetch(p.payload) for p in prts]:
        recursive_update(ctx, context)

    # extract settings from ctx to make handling easier
    settings = {}
    keys = []
    for key, value in ctx.items():
        if isinstance(value, collections.Mapping):
            settings[key] = value
            keys.append(key)
    for settingsKey in keys:
        del ctx[settingsKey]

    ctx = resolve(ctx)
    assert all(k.startswith(base.VAR_MARK) for k in ctx.keys()), ctx
    assert not any(v.startswith(base.VAR_MARK) for v in ctx.values()), ctx
    # TODO this needs to be done nested also
    # settings = resolve(settings)
    return ctx, settings


def fetch(content: str) -> dict:
    """Read all variables from content into a nested mapping.

    Additionally to the normal settings this is used to communicate settings
    from partials to i3configger.

    The settings:

        set $set_setting key=value otherKey=otherValue
        set $set_otherSetting key=value otherKey=otherValue

    will end up in a dict of dicts like:

        {
            'setting': {'key': 'value', 'otherKey': 'otherValue'},
            'otherSetting': {'key': 'value', 'otherKey': 'otherValue'}
        }
    """
    ctx = {}
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith(SET_MARK):
            continue
        payload = line.split(maxsplit=1)[1]
        if SETTINGS_MARK in payload:
            setter, keyValues = payload.split(maxsplit=1)
            dictName = base.VAR_MARK + setter[len(SETTINGS_MARK):]
            if dictName not in ctx:
                ctx[dictName] = {}
            for pair in keyValues.split():
                key, value = pair.split('=')
                ctx[dictName][key.strip()] = value.strip()
        else:
            key, value = payload.split(maxsplit=1)
            ctx[key] = value
    return ctx


def recursive_update(target, source):
    for k, v in source.items():
        if isinstance(v, collections.Mapping):
            r = recursive_update(target.get(k, {}), v)
            target[k] = r
        else:
            target[k] = source[k]
    return target


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
