import pprint
import re
import logging
import socket
import typing as t
from functools import total_ordering
from pathlib import Path

from i3configger import exc, base

log = logging.getLogger(__name__)

SPECIAL_SELECTORS = {
    "hostname": socket.gethostname()
}


@total_ordering
class Partial:
    CONTINUATION_RE = re.compile(r'\\\s*?\\s*?\n')
    COMMENT_MARK = '#'
    END_OF_LINE_COMMENT_MARK = ' # '
    DEFAULT_NAME = 'default'

    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.name
        self.selectors = self.path.stem.split('.')
        self.conditional = len(self.selectors) > 1
        self.key = self.selectors[0] if self.conditional else None
        self.value = self.selectors[1] if self.conditional else None

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    def __lt__(self, other):
        return self.name < other.name

    @property
    def isDefault(self) -> bool:
        if self.value == self.DEFAULT_NAME:
            return True
        return False

    @property
    def display(self) -> str:
        if not self.filtered:
            return ""
        return "### %s ###\n%s\n\n" % (self.path.name, self.filtered)

    @property
    def filtered(self) -> str:
        filtered = []
        for line in self._joined.splitlines():
            l = line.strip()
            if not l:
                continue
            if (not l.startswith(base.SET_MARK)
                    and not l.startswith(self.COMMENT_MARK)):
                filtered.append(line)
        return '\n'.join(filtered)

    @property
    def payload(self) -> str:
        """Strip empty lines, comment lines, and end of line comments."""
        prunes = []
        for line in self._joined.splitlines():
            l = line.strip()
            if not l:
                continue
            if l.startswith(self.COMMENT_MARK):
                continue
            line = line.rsplit(self.END_OF_LINE_COMMENT_MARK, maxsplit=1)[0]
            prunes.append(line)
        return '\n'.join(prunes)

    # FIXME I think this does not do anything
    @property
    def _joined(self) -> str:
        """Join line continuations.

        https://i3wm.org/docs/userguide.html#line_continuation"""
        return re.sub(self.CONTINUATION_RE, ' ', self._raw)

    @property
    def _raw(self) -> str:
        return self.path.read_text()


def find(prts: t.List[Partial], key: str, value: str) -> Partial:
    for prt in prts:
        if prt.key == key and prt.value == value:
            return prt


def select(partials: t.List[Partial],
           selector: t.Union[None, dict],
           excludes: t.Union[None, t.List[str]]=None,
           unconditionals=True, defaults=True, savedSelector=None) \
        -> t.Union[None, Partial, t.List[Partial]]:
    def _select():
        selected.append(partial)
        if partial.key in selector:
            del selector[partial.key]

    selected = []
    for partial in partials:
        if partial.conditional:
            if excludes and partial.key in excludes:
                log.debug("[IGNORE] %s (in %s)", partial, excludes)
                continue
            if (selector and partial.key in selector and
                    partial.value == selector.get(partial.key)):
                _select()
            elif defaults and partial.isDefault:
                _select()
            elif (partial.key in SPECIAL_SELECTORS and
                    partial.value == SPECIAL_SELECTORS[partial.key]):
                _select()
            else:
                try:
                    if savedSelector[partial.key] == partial.value:
                        _select()
                except KeyError:
                        pass
        elif unconditionals:
            _select()
    log.debug("selected:\n%s", pprint.pformat(selected))
    if selector:
        raise exc.ConfigError("not all selector processed: %s", selector)
    return selected[0] if len(selected) == 1 else selected


def create(sourcePath: Path, suffix: str) -> t.List[Partial]:
    prts = [Partial(p) for p in sourcePath.glob('*%s' % suffix)]
    if not prts:
        raise exc.I3configgerException(
            "no partials found at %s with suffix '%s'", sourcePath, suffix)
    return sorted(prts)
