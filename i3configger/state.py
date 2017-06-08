import logging

from i3configger import config, exc, partials

log = logging.getLogger(__name__)


I3STATUS = "i3status"
"""reserved key for status bar setting files"""
SELECT_NEXT = "select-next"
SELECT_PREVIOUS = "select-previous"
SELECT = "select"
SET = "set"
_ALL = [SELECT_NEXT, SELECT_PREVIOUS, SELECT, SET]
DEL = 'del'


# TODO if select has no candidate -> print possible candidates
# TODO if trying to set a non existing variable -> crash
def process(statePath, prts, message):
    state = fetch(statePath, prts)
    if not message:
        return state
    command, key, *rest = message
    value = rest[0] if rest else None
    log.debug(f"sending message {message} to {statePath}")
    if command == SET:
        # TODO make i3configger set <bars>:<bar id>:bar_mode docked  possible
        # TODO enhance this to access nested keys like
        # key:deeper:deepest -> state["set"][key][deeper][deepest]
        if value.lower() == DEL:
            del state["set"][key]
        else:
            state["set"][key] = value
    else:
        if command in [SELECT_NEXT, SELECT_PREVIOUS]:
            candidates = partials.find(prts, key)
            if not candidates:
                raise exc.MessageError(
                    f"No candidates for {message} in {prts}")
            if command == SELECT_PREVIOUS:
                candidates = reversed(candidates)
            current = state["select"].get(key) or candidates[0].key
            for idx, candidate in enumerate(candidates):
                if candidate.value == current:
                    try:
                        new = candidates[idx + 1]
                    except IndexError:
                        new = candidates[0]
                    log.info("select %s.%s", key, new)
                    state["select"][key] = new.value
                    break
        elif command == SELECT:
            candidates = partials.find(prts, key)
            if not candidates:
                raise exc.MessageError(
                    f"No candidates for {message} in {prts}")
            candidate = partials.find(prts, key, value)
            if not candidate:
                raise exc.MessageError(
                    f"No candidates for {message} in {candidates}")
            if value.lower == DEL:
                del state["select"][key]
            else:
                state["select"][key] = candidate.value
    config.freeze(statePath, state)
    return state


def fetch(statePath, prts):
    if not statePath.exists():
        initialState = create_initial_state(prts)
        config.freeze(statePath, initialState)
    return config.fetch(statePath)


def create_initial_state(prts):
    """fetch first of each selectable partials to have a sane state"""
    selects = {}
    for prt in prts:
        if not prt.needsSelection:
            continue
        if prt.key not in selects and prt.key != I3STATUS:
            selects[prt.key] = prt.value
    state = dict(select=selects, set={})
    return state
