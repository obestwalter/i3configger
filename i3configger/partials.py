import logging
import pprint
import re
import socket
import typing as t
from functools import total_ordering
from pathlib import Path

from i3configger import base, exc

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
        self.name = self.path.stem
        self.selectors = self.path.stem.split('.')
        self.needsSelection = len(self.selectors) > 1
        self.key = self.selectors[0] if self.needsSelection else None
        self.value = self.selectors[1] if self.needsSelection else None

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    def __lt__(self, other):
        return self.name < other.name

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


def find(prts: t.List[Partial], key: str, value: str= None) \
        -> t.Union[Partial, t.List[Partial]]:
    findings = []
    for prt in prts:
        if prt.key != key:
            continue
        if prt.value == value:
            return prt
        elif not value:
            findings.append(prt)
    return findings


def select(partials: t.List[Partial],
           selection: t.Optional[dict],
           excludes: t.Union[None, t.List[str], t.Set[str]]=None) \
        -> t.Union[None, Partial, t.List[Partial]]:
    def _select():
        selected.append(partial)
        if partial.needsSelection:
            del selection[partial.key]

    selected = []
    for partial in partials:
        if partial.needsSelection:
            if excludes and partial.key in excludes:
                log.debug("[IGNORE] %s (in %s)", partial, excludes)
                continue
            if (selection and partial.key in selection and
                    partial.value == selection.get(partial.key)):
                _select()
            elif (partial.key in SPECIAL_SELECTORS and
                    partial.value == SPECIAL_SELECTORS[partial.key]):
                _select()
        else:
            _select()
    log.debug("selected:\n%s", pprint.pformat(selected))
    if selection:
        raise exc.ConfigError(
            "selection processed incompletely: %s", selection)
    return selected[0] if len(selected) == 1 else selected


def create(partialsPath: Path) -> t.List[Partial]:
    prts = [Partial(p) for p in partialsPath.glob('*%s' % base.SUFFIX)]
    if not prts:
        raise exc.PartialsError(f"no '*{base.SUFFIX}' at {partialsPath}")
    return sorted(prts)
