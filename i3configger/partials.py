import re
import logging
import typing as t
from functools import total_ordering
from pathlib import Path

from i3configger import exc

log = logging.getLogger(__name__)


@total_ordering
class Partial:
    CONTINUATION_RE = re.compile(r'\\\s*?\\s*?\n')
    COMMENT_MARK = '#'
    END_OF_LINE_COMMENT_MARK = ' # '
    DEFAULT_NAME = 'default'
    DEFAULT_MARKER = '# i3configger default'
    STATUS_MARKER = 'i3status'

    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.name
        self.selectors = self.path.stem.split('.')
        self.conditional = len(self.selectors) > 1
        self.key = self.selectors[0] if self.conditional else None
        self.value = self.selectors[1] if self.conditional else None
        self.rendered = None

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    def __lt__(self, other):
        return self.name < other.name

    @property
    def isDefault(self) -> bool:
        assert self.conditional, self
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

    @property
    def _raw(self) -> str:
        return self.path.read_text()


def create(sourcePath: Path, suffix: str) -> t.List[Partial]:
        return sorted([Partial(p) for p in sourcePath.glob('*%s' % suffix)])


def select(prts: t.List[Partial], selectorMap: t.Union[None, dict]
           ) -> t.List[Partial]:
    def _select():
        selected.append(partial)
        if partial.key in selectorMap:
            del selectorMap[partial.key]

    selected: t.List[Partial] = []
    selectorMap = selectorMap or {}
    for partial in prts:
        if not partial.conditional:
            _select()
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
