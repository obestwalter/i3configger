import logging
import pprint
import socket
import typing as t
from functools import total_ordering
from pathlib import Path

from i3configger import base, exc

log = logging.getLogger(__name__)

# TODO document this
SPECIAL_SELECTORS = {
    "hostname": socket.gethostname()
}
# TODO document this
EXCLUDE_MARKER = "."
"""config files starting with a dot are always excluded"""


@total_ordering
class Partial:
    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.stem
        self.selectors = self.name.split('.')
        self.needsSelection = len(self.selectors) > 1
        self.key = self.selectors[0] if self.needsSelection else None
        self.value = self.selectors[1] if self.needsSelection else None
        self.lines = self.path.read_text().splitlines()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    def __lt__(self, other):
        return self.name < other.name

    @property
    def display(self) -> t.Optional[str]:
        lines = [l for l in self.lines
                 if not l.strip().startswith(base.SET_MARK)]
        if not lines:
            return
        return "### %s ###\n%s\n\n" % (self.path.name, "\n".join(lines))

    @property
    def context(self):
        ctx = {}
        for line in [l.strip() for l in self.lines
                     if l.strip().startswith(base.SET_MARK)]:
            payload = line.split(maxsplit=1)[1]
            key, value = payload.split(maxsplit=1)
            ctx[key] = value
        return ctx


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


def select(partials, selection, excludes=None) -> t.List[Partial]:
    def _select():
        selected.append(partial)
        if partial.needsSelection:
            del selection[partial.key]

    for key, value in SPECIAL_SELECTORS.items():
        if key not in selection:
            selection[key] = value
    selected = []
    for partial in partials:
        if partial.needsSelection:
            if excludes and partial.key in excludes:
                log.debug("[IGNORE] %s (in %s)", partial, excludes)
                continue
            if (selection and partial.key in selection and
                    partial.value == selection.get(partial.key)):
                _select()
        else:
            _select()
    log.debug("selected:\n%s", pprint.pformat(selected))
    if selection and not all(k in SPECIAL_SELECTORS for k in selection):
        raise exc.ConfigError(
            "selection processed incompletely: %s", selection)
    return selected


def create(partialsPath) -> t.List[Partial]:
    partialsPath = Path(partialsPath)
    assert partialsPath.is_dir(), partialsPath
    prts = []
    for path in partialsPath.glob('*%s' % base.SUFFIX):
        if path.name.startswith(EXCLUDE_MARKER):
            log.info(f"excluding {path} because it starts with a dot")
            continue
        prts.append(Partial(path))
    if not prts:
        raise exc.PartialsError(f"no '*{base.SUFFIX}' at {partialsPath}")
    return sorted(prts)
