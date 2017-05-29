import re
import logging
import typing as t
from functools import total_ordering
from pathlib import Path

from i3configger import base, exc

log = logging.getLogger(__name__)


@total_ordering
class Partial:
    CONTINUATION_RE = re.compile(r'\\\s*?\\s*?\n')
    COMMENT_MARK = '#'
    END_OF_LINE_COMMENT_MARK = ' # '
    DEFAULT_NAME = 'default'
    DEFAULT_MARKER = '# i3configger default'

    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.name
        self.selectors = self.path.stem.split('.')
        self.i3status = self.selectors[0] == base.I3STATUS_BAR_MARKER
        self.conditional = len(self.selectors) > 1 and not self.i3status
        if self.i3status:
            self.key = self.selectors[1]
            try:
                self.value = self.selectors[2]
            except IndexError:
                self.value = None
        elif self.conditional:
            self.key = self.selectors[0]
            self.value = self.selectors[1]
        else:
            self.key = None
            self.value = None
        self._raw = self.path.read_text()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    def __lt__(self, other):
        return self.name < other.name

    @property
    def isDefault(self) -> bool:
        if self.value == self.DEFAULT_NAME:
            return True
        if self.DEFAULT_MARKER in self._raw:
            return True
        return False

    @property
    def prepared(self) -> str:
        return "### %s ###\n%s\n\n" % (self.path.name, self.payload)

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

    @property
    def _joined(self) -> str:
        """Join line continuations.

        https://i3wm.org/docs/userguide.html#line_continuation"""
        return re.sub(self.CONTINUATION_RE, ' ', self._raw)


def get_content(prts: t.List[Partial], selectorMap: dict,
                excludes: t.Union[None, t.List]=None) -> str:
    selected = select(prts, selectorMap, excludes)
    return ''.join(p.prepared for p in selected)


def find(prts: t.List[Partial], key: str, value: str) -> Partial:
    for prt in prts:
        if prt.key == key and prt.value == value:
            return prt


def select(prts: t.List[Partial], selectorMap: t.Union[None, dict],
           excludes: t.Union[None, t.List]=None) -> t.List[Partial]:
    def _select():
        selected.append(partial)
        if partial.key in selectorMap:
            del selectorMap[partial.key]

    selectorMap = selectorMap or {}
    excludes = excludes or []
    selected = []
    for partial in prts:
        if not partial.conditional:
            _select()
        if partial.key in excludes:
            log.debug("[IGNORE] %s (in %s)", partial, excludes)
            continue
        else:
            if partial.key in selectorMap:
                if partial.value == selectorMap.get(partial.key):
                    _select()
            else:
                if partial.isDefault:
                    _select()
    if selectorMap:
        raise exc.SelectError("not all selectors processed: %s", selectorMap)
    return selected


def create(sourcePath: Path, suffix: str) -> t.List[Partial]:
        return sorted([Partial(p) for p in sourcePath.glob('*%s' % suffix)])
