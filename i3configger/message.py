import logging
from pathlib import Path

from i3configger import base, config, exc, partials, context

log = logging.getLogger(__name__)


I3STATUS = "i3status"
"""reserved key for status bar setting files"""
DEL = 'del'
"""signal to delete a key in shadow or set"""


class CMD:
    SELECT_NEXT = "select-next"
    SELECT_PREVIOUS = "select-previous"
    SELECT = "select"
    SET = "set"
    MERGE = "merge"
    PRUNE = "prune"
    SHADOW = "shadow"

    @classmethod
    def get_all_commands(cls):
        return [v for k, v in cls.__dict__.items()
                if k[0].isupper() and k[0] != '_']


def process(messagesPath, prts, message):
    mp = Messenger(messagesPath, prts, message)
    mp.execute()
    config.freeze(messagesPath, mp.payload)


class Messenger:
    def __init__(self, messagesPath, prts, message=None):
        self.messagesPath = messagesPath
        self.prts = prts
        self.message = message
        if self.message:
            self.command, self.key, *rest = message
            self.value = rest[0] if rest else ''
            if self.command != CMD.SHADOW and ':' in self.key:
                raise exc.UserError(
                    f"nesting of keys only sensible with {CMD.SHADOW}")
        log.debug(f"sending message {message} to {messagesPath}")

    def execute(self):
        self.payload = self.fetch_messages()
        try:
            {
                CMD.MERGE: self._process_merge,
                CMD.PRUNE: self._process_prune,
                CMD.SET: self._process_set,
                CMD.SELECT: self._process_select,
                CMD.SHADOW: self._process_shadow,
                CMD.SELECT_NEXT: self._process_select_shift,
                CMD.SELECT_PREVIOUS: self._process_select_shift,
            }[self.command]()
        except KeyError:
            raise exc.UserError(
                f"Unknown command: {self.command}. "
                f"Use one of {', '.join(CMD.get_all_commands())}")

    def _process_merge(self):
        self._transform(context.merge)

    def _process_prune(self):
        self._transform(context.prune)

    def _transform(self, func):
        path = Path(self.key).expanduser()
        if not path.is_absolute():
            path = self.messagesPath.parent / path
        self.payload = func(self.payload, config.fetch(path))

    def _process_set(self):
        if self.value.lower() == DEL:
            del self.payload[CMD.SET][base.VAR_MARK + self.key]
        else:
            self.payload[CMD.SET][base.VAR_MARK + self.key] = self.value

    def _process_select(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(
                f"No candidates for {self.message} in {self.prts}")
        candidate = partials.find(self.prts, self.key, self.value)
        if not candidate:
            raise exc.MessageError(
                f"No candidates for {self.message} in {candidates}")
        if self.value and self.value.lower() == DEL:
            del self.payload[CMD.SELECT][self.key]
        else:
            self.payload[CMD.SELECT][self.key] = candidate.value

    def _process_shadow(self):
        """Shadow arbitrary settings made in i3configger.json.

        key:deeper:deepest[...] -> [key][deeper][deepest][...]
        """
        parts = self.key.split(':')
        current = self.payload[CMD.SHADOW]
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
        current = self.payload["select"].get(self.key) or candidates[0].key
        for idx, candidate in enumerate(candidates):
            if candidate.value == current:
                try:
                    new = candidates[idx + 1]
                except IndexError:
                    new = candidates[0]
                break
        else:
            new = candidates[0]
        log.info("select %s.%s", self.key, new)
        self.payload[CMD.SELECT][self.key] = new.value

    def fetch_messages(self):
        if not self.messagesPath.exists():
            messages = {}
        else:
            messages = config.fetch(self.messagesPath)
        self.ensure_message_keys(messages, self.prts)
        return messages

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
