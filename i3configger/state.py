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


class MessageProcessor:
    def __init__(self, statePath, prts, message):
        self.statePath = statePath
        self.prts = prts
        self.message = message
        self.state = self.fetch_state()
        if self.message:
            self.command, self.key, *rest = message
            self.value = rest[0] if rest else None
        log.debug(f"sending message {message} to {statePath}")

    def process(self):
        """process message and persist it"""
        if not self.message:
            return self.state
        {
            SET: self._process_set,
            SELECT: self._process_select,
            SELECT_NEXT: self._process_select_shift,
            SELECT_PREVIOUS: self._process_select_shift,
        }[self.command]()

    def _process_set(self):
        # TODO make i3configger set <bars>:<bar id>:bar_mode docked  possible
        # enhance this to access nested keys like
        # key:deeper:deepest -> state["set"][key][deeper][deepest]
        # need to write nested state in set dict that gets fetched later
        if self.value.lower() == DEL:
            del self.state["set"][self.key]
        else:
            self.state["set"][self.key] = self.value

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
            del self.state["select"][self.key]
        else:
            self.state["select"][self.key] = candidate.value

    def _process_select_shift(self):
        candidates = partials.find(self.prts, self.key)
        if not candidates:
            raise exc.MessageError(
                f"No candidates for {self.message} in {self.prts}")
        if self.command == SELECT_PREVIOUS:
            candidates = reversed(candidates)
        current = self.state["select"].get(self.key) or candidates[0].key
        for idx, candidate in enumerate(candidates):
            if candidate.value == current:
                try:
                    new = candidates[idx + 1]
                except IndexError:
                    new = candidates[0]
                log.info("select %s.%s", self.key, new)
                self.state["select"][self.key] = new.value
                break

    def fetch_state(self):
        if not self.statePath.exists():
            initialState = self._create_initial_state(self.prts)
            config.freeze(self.statePath, initialState)
        return config.fetch(self.statePath)

    @staticmethod
    def _create_initial_state(prts):
        """fetch first of each selectable partials to have a sane state"""
        selects = {}
        for prt in prts:
            if not prt.needsSelection:
                continue
            if prt.key not in selects and prt.key != I3STATUS:
                selects[prt.key] = prt.value
        state = dict(select=selects, set={})
        return state
