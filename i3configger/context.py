import logging
import typing as t
from string import Template

from i3configger import base, exc, partials

log = logging.getLogger(__name__)


def merge(item: t.Iterable[t.Union[dict, partials.Partial]]) -> dict:
    """Take items, merge contexts, resolve and clean them variables"""
    ctx = {}
    for elem in item:
        if not isinstance(elem, dict):
            elem = elem.context
        ctx.update(elem)
    ctx = resolve_variables(ctx)
    ctx = remove_variable_markers(ctx)
    return ctx


def remove_variable_markers(ctx: dict) -> dict:
    cleaned = {}
    lvm = len(base.VAR_MARK)
    for key, value in ctx.items():
        key = key[lvm:] if key.startswith(base.VAR_MARK) else key
        cleaned[key] = value
    return cleaned


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


def substitute(content, ctx):
    """Substitute all variables with their values.

    Works out of the box, because '$' is the standard substitution
    marker for string.Template
    """
    return Template(content).safe_substitute(ctx)
