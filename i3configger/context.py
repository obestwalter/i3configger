import logging
from functools import reduce
from string import Template
from typing import Iterable, Union

from i3configger import config, exc, partials

log = logging.getLogger(__name__)


def process(item: Iterable[Union[dict, partials.Partial]]) -> dict:
    ctx = merge_all(item)
    ctx = resolve_variables(ctx)
    ctx = remove_variable_markers(ctx)
    return ctx


def merge_all(item: Iterable[Union[dict, partials.Partial]]) -> dict:
    """Merge contexts of an arbitrary number of items."""
    dicts = []
    for elem in item:
        dicts.append(elem if isinstance(elem, dict) else elem.context)
    return reduce(merge, dicts)


def merge(dst: dict, src: dict) -> dict:
    """merge source into destination mapping (overwrite existing keys)."""
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


def resolve_variables(ctx: dict) -> dict:
    """If variables are set by a variable, replace them by their value."""
    while any(v.startswith(config.MARK.VAR) for v in ctx.values()):
        for key, value in ctx.items():
            if value.startswith(config.MARK.VAR):
                ctx[key] = _resolve_variable(value, ctx, path=key)
    return ctx


def _resolve_variable(key, ctx, path):
    path += "->" + key
    resolved = ctx.get(key)
    if not resolved:
        raise exc.ContextError(f"not resolvable: {path}")
    if resolved.startswith(config.MARK.VAR):
        return _resolve_variable(resolved, ctx, path)
    return resolved


def remove_variable_markers(ctx: dict) -> dict:
    cleaned = {}
    lvm = len(config.MARK.VAR)
    for key, value in ctx.items():
        key = key[lvm:] if key.startswith(config.MARK.VAR) else key
        cleaned[key] = value
    return cleaned


def substitute(content: str, ctx: dict):
    """Substitute all variables with their values.

    Works out of the box, because '$' is the standard substitution
    marker for string.Template

    As there also might be other occurrences of "$" (e.g. in regexes)
    `safe_substitute()` is used,
    """
    return Template(content).safe_substitute(ctx)
