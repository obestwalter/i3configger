"""Functionality implementing the messaging mechanism."""
import logging
from pathlib import Path

from i3configger import base, config, context, exc, partials

log = logging.getLogger(__name__)


class CMD:
    MERGE = "merge"
    PRUNE = "prune"
    SELECT = "select"
    SELECT_NEXT = "select-next"
    SELECT_PREVIOUS = "select-previous"
    SET = "set"
    SHADOW = "shadow"

    @classmethod
    def get_all_commands(cls):
        return [v for k, v in cls.__dict__.items() if k[0].isupper() and k[0] != "_"]


def save(message):
    cnf = config.I3configgerConfig(load=False)
    prts = partials.create(cnf.partialsPath)
    messenger = Messenger(cnf.messagesPath, prts, message)
    messenger.digest_message()
    config.freeze(cnf.messagesPath, messenger.payload)


class Messenger:
    def __init__(self, messagesPath, prts, message=None):
        self.messagesPath = messagesPath
        self.prts = prts
        self.message = message
        if message:
            if len(message) < 2:
                raise exc.UserError(f"message needs at least key and value ({message})")
            self.command, self.key, *rest = message
            self.value = rest[0] if rest else ""
            if self.command != CMD.SHADOW and ":" in self.key:
                raise exc.UserError(f"nesting of keys only sensible with {CMD.SHADOW}")
        self.payload = self.fetch_messages()
        log.debug(f"send message '{message}' to {messagesPath}")

    def digest_message(self):
        try:
            self.COMMAND_METHOD_MAP[self.command]()
        except KeyError:
            raise exc.UserError(
                f"Unknown command: {self.command}. "
                f"Use one of {', '.join(CMD.get_all_commands())}"
            )

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
        if self.value.lower() == base.DEL:
            del self.payload[CMD.SET][base.VAR_MARK + self.key]
        else:
            self.payload[CMD.SET][base.VAR_MARK + self.key] = self.value

    def _process_select(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(f"No candidates for {self.message} in {self.prts}")
        candidate = partials.find(self.prts, self.key, self.value)
        if not candidate:
            raise exc.MessageError(f"No candidates for {self.message} in {candidates}")
        if self.value and self.value.lower() == base.DEL:
            del self.payload[CMD.SELECT][self.key]
        else:
            self.payload[CMD.SELECT][self.key] = candidate.value

    def _process_shadow(self):
        """Shadow arbitrary settings made in i3configger.json.

        key:deeper:deepest[...] -> [key][deeper][deepest][...]
        """
        parts = self.key.split(":")
        current = self.payload[CMD.SHADOW]
        while True:
            part = parts.pop(0)
            if parts:
                current[part] = {}
                current = current[part]
            else:
                if self.value is not None and self.value.lower() == base.DEL:
                    del current[part]
                else:
                    current[part] = self.value
                break

    def _process_select_shift(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(f"No candidates for {self.message} in {self.prts}")
        if self.command == CMD.SELECT_PREVIOUS:
            candidates = list(reversed(candidates))
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
        log.info(f"select {self.key}.{new}")
        self.payload[CMD.SELECT][self.key] = new.value

    def fetch_messages(self):
        if self.messagesPath.exists():
            messages = config.fetch(self.messagesPath)
        else:
            messages = {}
        self.ensure_message_keys(messages, self.prts)
        return messages

    def ensure_message_keys(self, state, prts):
        if CMD.SELECT not in state:
            initialSelects = {}
            for prt in prts:
                if not prt.needsSelection:
                    continue
                if prt.key not in initialSelects and prt.key != base.I3BAR:
                    initialSelects[prt.key] = prt.value
            state[CMD.SELECT] = initialSelects
        if CMD.SET not in state:
            state[CMD.SET] = {}
        if CMD.SHADOW not in state:
            state[CMD.SHADOW] = {}

    COMMAND_METHOD_MAP = {
        CMD.MERGE: _process_merge,
        CMD.PRUNE: _process_prune,
        CMD.SELECT: _process_select,
        CMD.SELECT_NEXT: _process_select_shift,
        CMD.SELECT_PREVIOUS: _process_select_shift,
        CMD.SET: _process_set,
        CMD.SHADOW: _process_shadow,
    }
