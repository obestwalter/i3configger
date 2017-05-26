import logging
from collections import defaultdict
from pathlib import Path

from i3configger import defaults, exc, utils

log = logging.getLogger(__name__)
VAR_MARK = '$'
COMMENT_MARK = '#'
END_OF_LINE_COMMENT_MARK = ' # '
SET = 'set'
BINDCODE = 'bindcode'
BINDSYM = 'bindsym'
DEFAULT_KEY = 'default'


class ConfigCreator:
    def __init__(self, sourcePath=defaults.SOURCES_PATH,
                 suffix=defaults.SOURCE_SUFFIX):
        self.sourcePath = sourcePath
        self.suffix = suffix
        glob = '*%s' % self.suffix
        self.partials = [Partial(p) for p in self.sourcePath.glob(glob)]
        self.unconditionals = [p for p in self.partials if not p.isSelectable]

    def select(self, selectorMap=None):
        selected = []
        selectorMap = selectorMap or {}
        selectablesMap = self._make_selectables_map()
        # utils.embed()
        for k, innerMap in selectablesMap.items():
            if k not in selectorMap:
                log.warning("no selector for %s - trying default", k)
                key = DEFAULT_KEY
            else:
                key = selectorMap[k]
            partial = innerMap.get(key)
            if not partial:
                log.warning("no partial for %s in %s", key, innerMap)
            else:
                selected.append(partial)
        return selected

    def _make_selectables_map(self):
        map_ = defaultdict(dict)
        for p in self.partials:
            if not p.isSelectable:
                continue
            map_[p.key][p.value] = p
        return map_


class Partial:
    def __init__(self, path: Path):
        self.path = path
        self.selectors = self.path.stem.split('.')
        if self.isSelectable:
            self.key = self.selectors[0]
            self.value = self.selectors[1]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __str__ = __repr__

    @property
    def isSelectable(self):
        return len(self.selectors) > 1

    def fits_selector(self, selector):
        pass

    @property
    def rendered(self, context):
        raise NotImplementedError

    @property
    def context(self):
        exp = 0
        for line in self.prunedLines:
            if Context.is_assignment(line):
                exp += 1
        context = Context(self.prunedLines)
        if len(context) != exp:
            raise exc.ParseError("expected %s assignments - got %s for %s",
                                 exp, len(context), self.clean)
        return context

    @property
    def bindings(self):
        exp = 0
        for line in self.prunedLines:
            if Bindings.sets_binding(line):
                exp += 1
        bindings = Bindings(self.prunedLines)
        if len(bindings) != exp:
            raise exc.ParseError("expected %s bindings - got %s for %s",
                                 exp, len(bindings), self.clean)
        return bindings

    @property
    def clean(self):
        return '\n'.join(self.prunedLines)

    @property
    def _raw(self):
        return self.path.read_text()

    @property
    def _lines(self):
        return self._raw.splitlines()

    @property
    def prunedLines(self):
        """Strip empty lines, comments and end of line comments"""
        strippedOfAllCruft = []
        for line in self._lines:
            line = line.strip()
            line = line.rsplit(END_OF_LINE_COMMENT_MARK, maxsplit=1)[0]
            if line:
                strippedOfAllCruft.append(line)
        return strippedOfAllCruft


class Context:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.dict)

    @property
    def dict(self):
        context = {}
        for line in self.lines:
            if not line.startswith(SET):
                continue
            key, value = line.split(maxsplit=2)[1:]
            context[key] = value
        return context

    def for_substitution(self, greaterContext):
        resolvedContext = self.resolve(greaterContext)
        return {k[len(VAR_MARK):]: v for k, v in resolvedContext.items()}

    def resolve(self, greaterContext):
        context = self.dict
        seenKeys = []
        for key, value in self.dict.items():
            if key in seenKeys:
                raise exc.DuplicateKey("%s -> %s would be overridden with %s",
                                       key, context[key], value)
            if value.startswith('$'):
                try:
                    context[key] = greaterContext[value]
                except KeyError:
                    log.exception("[IGNORED] %s, %s", key, value)
        return context

    def needs_resolution(self):
        return any(v.startswith(VAR_MARK) for v in self.dict.values())

    @staticmethod
    def is_assignment(line):
        return line.startswith(SET)


class Bindings:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.dict)

    @property
    def dict(self):
        context = {}
        for line in self.lines:
            if not Bindings.sets_binding(line):
                continue
            maxsplit = 3 if '--release' in line else 2
            bindType, shortcut, binding = line.split(maxsplit=maxsplit)
            context["%s:%s" % (bindType, shortcut)] = binding
        return context

    @staticmethod
    def sets_binding(line):
        return line.startswith(BINDSYM) or line.startswith(BINDCODE)


if __name__ == '__main__':
    sourcesPath = Path(__file__).parent / 'examples' / 'big'
    cc = ConfigCreator()
    cc.select()
    # for p in cc.partials:
    #     print(p.path)
    #     print(p.clean)
    #     print()
    #     print(p.context.dict)
    #     print(p.bindings.dict)
    #     print()
