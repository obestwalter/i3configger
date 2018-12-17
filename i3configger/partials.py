import logging
import pprint
import socket
from functools import total_ordering
from pathlib import Path
from typing import Union, List

from i3configger import base, exc

log = logging.getLogger(__name__)

SPECIAL_SELECTORS = {"hostname": socket.gethostname()}
EXCLUDE_MARKER = "."
"""config files starting with a dot are always excluded"""


@total_ordering
class Partial:
    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.stem
        self.selectors = self.name.split(".")
        self.needsSelection = len(self.selectors) > 1
        self.key = self.selectors[0] if self.needsSelection else None
        self.value = self.selectors[1] if self.needsSelection else None
        self.lines = self.path.read_text().splitlines()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path.name})"

    def __lt__(self, other):
        return self.name < other.name

    def get_pruned_content(self) -> str:
        """pruned content or '' if file only contains vars and comments"""
        lines = [l for l in self.lines if not l.strip().startswith(base.SET_MARK)]
        if not self.contain_something(lines):
            return ""
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        joinedLines = "\n".join(lines)
        return f"### {self.path.name} ###\n{joinedLines}\n\n"

    @staticmethod
    def contain_something(lines):
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(base.COMMENT_MARK):
                continue
            if line.startswith(base.SET_MARK):
                continue
            return True

    @property
    def context(self):
        ctx = {}
        for line in [
            l.strip() for l in self.lines if l.strip().startswith(base.SET_MARK)
        ]:
            payload = line.split(maxsplit=1)[1]
            key, value = payload.split(maxsplit=1)
            ctx[key] = value
        return ctx


def find(
    prts: List[Partial], key: str, value: str = None
) -> Union[Partial, List[Partial]]:
    findings = []
    for prt in prts:
        if prt.key != key:
            continue
        if prt.value == value:
            return prt
        elif not value:
            findings.append(prt)
    return findings


def select(partials, selection, excludes=None) -> List[Partial]:
    def _select():
        selected.append(partial)
        if partial.needsSelection:
            del selection[partial.key]

    for key, value in SPECIAL_SELECTORS.items():
        if key not in selection:
            selection[key] = value
    selected: List[Partial] = []
    for partial in partials:
        if partial.needsSelection:
            if excludes and partial.key in excludes:
                log.debug(f"[IGNORE] {partial} (in {excludes})")
                continue
            if (
                selection
                and partial.key in selection
                and partial.value == selection.get(partial.key)
            ):
                _select()
        else:
            _select()
    log.debug(f"selected:\n{pprint.pformat(selected)}")
    if selection and not all(k in SPECIAL_SELECTORS for k in selection):
        raise exc.ConfigError(f"selection processed incompletely: {selection}")
    return selected


def create(partialsPath) -> List[Partial]:
    partialsPath = Path(partialsPath)
    assert partialsPath.is_dir(), partialsPath
    prts = []
    for path in partialsPath.glob(f"*{base.SUFFIX}"):
        if path.name.startswith(EXCLUDE_MARKER):
            log.info(f"excluding {path} because it starts with {EXCLUDE_MARKER}")
            continue
        prts.append(Partial(path))
    if not prts:
        raise exc.PartialsError(f"no '*{base.SUFFIX}' at {partialsPath}")
    return sorted(prts)
