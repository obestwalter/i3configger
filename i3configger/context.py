import logging
import typing as t
from functools import reduce
from string import Template

from i3configger import base, exc, partials

log = logging.getLogger(__name__)


def process(item: t.Iterable[t.Union[dict, partials.Partial]]) -> dict:
    """merge contexts of an arbitrary number of items"""
    dicts = []
    for elem in item:
        dicts.append(elem if isinstance(elem, dict) else elem.context)
    return reduce(merge, dicts)


def merge(dst: dict, src: dict) -> dict:
    """merge source into destination mapping (overwrite existing keys)"""
    for key in src:
        if key in dst:
            if isinstance(dst[key], dict) and isinstance(src[key], dict):
                merge(dst[key], src[key])
            else:
                dst[key] = src[key]
        else:
            dst[key] = src[key]
    return dst


def prune(dst: dict, src: dict) -> dict:
    for key, value in src.items():
        if isinstance(value, dict):
            prune(dst.get(key, {}), value)
        elif key in dst:
            del dst[key]
    return dst


def resolve_variables(context: dict) -> dict:
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


def remove_variable_markers(ctx: dict) -> dict:
    cleaned = {}
    lvm = len(base.VAR_MARK)
    for key, value in ctx.items():
        key = key[lvm:] if key.startswith(base.VAR_MARK) else key
        cleaned[key] = value
    return cleaned


def substitute(content: str, ctx: dict):
    """Substitute all variables with their values.

    Works out of the box, because '$' is the standard substitution
    marker for string.Template
    """
    return Template(content).safe_substitute(ctx)
