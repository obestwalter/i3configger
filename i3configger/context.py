import logging
import typing as t
from collections import defaultdict

from i3configger import exc, partials

log = logging.getLogger(__name__)
SET_MARK = 'set'
SETTINGS_MARK = '$i3configger_'
VAR_MARK = '$'


def create(prts: t.List[partials.Partial]) -> dict:
    merged = {}
    for context in [make(p.payload) for p in prts]:
        merged.update(context)
    resolvedContext = resolve(merged)
    return resolvedContext


def make(content: str) -> dict:
    ctx = {}
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith(SET_MARK):
            continue
        key, value = line.split(maxsplit=2)[1:]
        ctx[key] = value
    return ctx


def resolve(context: dict) -> dict:
    if not any(v.startswith(VAR_MARK) for v in context.values()):
        log.debug("needs no resolution: %s", context)
        return context
    resolvedContext = {}
    seenKeys = []
    for key, value in context.items():
        if key in seenKeys:
            raise exc.DuplicateKey("%s -> %s would be overridden with %s",
                                   key, map_[key], value)
        if value.startswith(VAR_MARK):
            try:
                resolvedContext[key] = context[value]
            except KeyError:
                log.exception("[IGNORED] %s, %s", key, value)
    return resolvedContext


def cleaned_for_substitution(context: dict) -> dict:
    """Remove var markers from keys"""
    return {k[len(VAR_MARK):]: v for k, v in context.items()}


def fetch_settings(context: dict) -> dict:
    """Simple way of communicating settings to i3configger

        set $i3configger_setting_key value
        set $i3configger_setting_otherVey otherValue
        set $i3configger_otherSetting_key value
        set $i3configger_otherSetting_otherKey otherValue

    will end up in a map of dicts like

        {
            'setting': {'key': 'value', 'otherKey': 'otherValue'},
            'otherSetting': {'key': 'value', 'otherKey': 'otherValue'}
        }
    """
    dictOfDicts = defaultdict(dict)
    for key, value in context.items():
        if not key.startswith(SETTINGS_MARK):
            continue
        _, dictName, dictKey = key.split('_')
        dictOfDicts[dictName][dictKey] = value
    return dictOfDicts
