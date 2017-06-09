import logging

from i3configger import config, exc, partials

log = logging.getLogger(__name__)


I3STATUS = "i3status"
"""reserved key for status bar setting files"""
# TODO document deletion for set and shadow
DEL = 'del'
"""signal to delete a key in shadow or set"""


class CMD:
    SELECT_NEXT = "select-next"
    SELECT_PREVIOUS = "select-previous"
    SELECT = "select"
    SET = "set"
    SHADOW = "shadow"


def process(statePath, prts, message):
    mp = Messenger(statePath, prts, message)
    mp.transform()
    config.freeze(statePath, mp.msg)


class Messenger:
    def __init__(self, messagesPath, prts, message=None):
        self.messagesPath = messagesPath
        self.prts = prts
        self.message = message
        self.msg = self.fetch_frozen_messages()
        if self.message:
            self.command, self.key, *rest = message
            self.value = rest[0] if rest else None
        log.debug(f"sending message {message} to {messagesPath}")

    def transform(self):
        """transform affected mapping"""
        {
            CMD.SET: self._process_set,
            CMD.SELECT: self._process_select,
            CMD.SHADOW: self._process_shadow,
            CMD.SELECT_NEXT: self._process_select_shift,
            CMD.SELECT_PREVIOUS: self._process_select_shift,
        }[self.command]()

    def _process_set(self):
        if self.value.lower() == DEL:
            del self.msg[CMD.SET][self.key]
        else:
            self.msg[CMD.SET][self.key] = self.value

    def _process_select(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(
                f"No candidates for {self.message} in {self.prts}")
        candidate = partials.find(self.prts, self.key, self.value)
        if not candidate:
            raise exc.MessageError(
                f"No candidates for {self.message} in {candidates}")
        if self.value.lower() == DEL:
            del self.msg[CMD.SELECT][self.key]
        else:
            self.msg[CMD.SELECT][self.key] = candidate.value

    # TODO document
    # TODO document nesting behaviour
    def _process_shadow(self):
        """Shadow arbitrary settings made in i3configger.json.

        key:deeper:deepest[...] -> [key][deeper][deepest][...]
        """
        parts = self.key.split(':')
        current = self.msg[CMD.SHADOW]
        while True:
            part = parts.pop(0)
            if parts:
                current[part] = {}
                current = current[part]
            else:
                if self.value is not None and self.value.lower() == DEL:
                    del current[part]
                else:
                    current[part] = self.value
                break

    def _process_select_shift(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(
                f"No candidates for {self.message} in {self.prts}")
        if self.command == CMD.SELECT_PREVIOUS:
            candidates = reversed(candidates)
        current = self.msg["select"].get(self.key) or candidates[0].key
        for idx, candidate in enumerate(candidates):
            if candidate.value == current:
                try:
                    new = candidates[idx + 1]
                except IndexError:
                    new = candidates[0]
                log.info("select %s.%s", self.key, new)
                self.msg[CMD.SELECT][self.key] = new.value
                break

    def fetch_frozen_messages(self):
        if not self.messagesPath.exists():
            state = {}
        else:
            state = config.fetch(self.messagesPath)
        self.ensure_message_keys(state, self.prts)
        config.freeze(self.messagesPath, state)
        return state

    def ensure_message_keys(self, state, prts):
        if CMD.SELECT not in state:
            initialSelects = {}
            for prt in prts:
                if not prt.needsSelection:
                    continue
                if prt.key not in initialSelects and prt.key != I3STATUS:
                    initialSelects[prt.key] = prt.value
            state[CMD.SELECT] = initialSelects
        if CMD.SET not in state:
            state[CMD.SET] = {}
        if CMD.SHADOW not in state:
            state[CMD.SHADOW] = {}
