import logging
import pprint
import time
import typing as t
from pathlib import Path
from string import Template

from i3configger import config, context, exc, partials

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, cnf: config.I3configgerConfig):
        self.cnf = cnf
        self.stagingPathMap = {}
        """staging path -> final location"""
        log.info("initialized %s", self)

    def __str__(self):
        return "%s\n%s" % (self.__class__.__name__, pprint.pformat(vars(self)))

    def build(self):
        if self.cnf.command:
            COMMAND.execute(self, command)

        targetPath = Path(self.cnf.settings['target'])
        name = self.cnf.settings['name']

        allPrts = partials.create(
            Path(self.cnf.settings['partials']), self.cnf.settings['suffix'])

        excludes = [self.cnf.marker] if self.cnf.hasStatusConfig else None
        selected = partials.select(
            allPrts, self.selectors, excludes, self.selectors)
        if not selected:
            raise exc.I3configgerException(
                "No content for %s, %s, %s", allPrts, self.selectors, excludes)
        ctx = context.create(selected)
        self.build_main(selected, ctx)
        if self.cnf.hasStatusConfig:
            self.build_i3status(allPrts, ctx)
        if self.buildIsOk():
            self.replace_configs()

    def build_main(self, prts, ctx):
        content = '\n'.join(prt.display for prt in prts)
        substituted = self.substitute(content, ctx)
        complete = "%s\n\n%s" % (self.get_header(), substituted)
        self.mainTargetPath.write_text(complete)

    def build_i3status(self, prts: t.List[partials.Partial], ctx: dict):
        self._build_bar_configs(prts, ctx)
        self._add_bar_settings(prts, ctx)

    def _add_bar_settings(self, prts, ctx):
        with self.mainTargetPath.open('a') as f:
            for barName, barCtx in self.cnf.bars.items():
                barCtx["id"] = barName
                prt = partials.find(prts, self.cnf.marker, barCtx[self.cnf.TEMPLATE])
                localCtx = dict(ctx)
                localCtx.update(barCtx)
                localCtx.update(context.create([prt]))
                cnt = self.substitute(prt.payload, localCtx)
                f.write(cnt + '\n')

    def _build_bar_configs(self, prts, ctx):
        allUsedSources = set([s[self.cnf.SOURCE] for s in self.cnf.bars.values()])
        for source in allUsedSources:
            prt = partials.find(prts, self.cnf.marker, source)
            assert isinstance(prt, partials.Partial), prt
            localCtx = dict(ctx)
            localCtx.update(context.create([prt]))
            sourceCnt = self.substitute(prt.payload, localCtx)
            targetRoot = Path(self.cnf.target).expanduser()
            targetPath = targetRoot / ("%s.%s.conf" % (self.cnf.marker, source))
            targetPath.write_text(sourceCnt)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        template = Template(content)
        renderedContent = template.safe_substitute(ctx)
        return renderedContent

    def get_header(self):
        msg = (f'# Generated from {self.sourcePath} by i3configger '
               f'({time.asctime()}) #')
        sep = "#" * len(msg)
        return "%s\n%s\n%s" % (sep, msg, sep)

    @property
    def buildIsOk(self):
        raise NotImplementedError()
        # check with i3 -C if config is o.k.

    def replace_configs(self):
        raise NotImplementedError()
        # Go through stagingMap and replace all files


class COMMAND:
    """commands issued from the command line can change the configuration,

    Tuple contains name and number of expected additional arguments
    """
    SELECT_NEXT = ("select-next", 1)
    SELECT_PREVIOUS = ("select-previous", 1)
    SELECT = ("select", 2)
    SET = ("set", 2)
    _ALL = [SELECT_NEXT, SELECT_NEXT, SELECT, SET]

    @staticmethod
    def _next(current, items: list):
        try:
            return items[items.index(current) + 1]
        except IndexError:
            return items[0]

    @staticmethod
    def _previous(current, items: list):
        try:
            return items[items.index(current) - 1]
        except IndexError:
            return items[-1]

    FUNC_MAP = {SELECT_NEXT: _next, SELECT_PREVIOUS: _previous}

    @classmethod
    def get_spec(cls, command):
        for c in cls._ALL:
            if c[0] == command:
                return c[1]
        raise exc.I3configgerException(f"unknown command: {command}")

    @classmethod
    def execute(cls,
                prts: t.List[partials.Partial],
                cnf: config.I3configgerConfig,
                command: list):
        action, key, *rest = command
        value = rest[0] if rest else None
        if action in [cls.SELECT_NEXT, cls.SELECT_PREVIOUS]:
            candidates = partials.find(prts, key)
            if not candidates:
                raise exc.CommandError(f"No candidates for {command}")
            current = cnf.select.get(key) or candidates[-1]
            new = cls.FUNC_MAP[action](current, candidates)
            cnf.select[key] = new.value
        elif action == cls.SELECT:
            candidate = partials.find(prts, key, value)
            if not candidate:
                raise exc.CommandError(f"No candidate for {command}")
            cnf.select[key] = candidate.value
        elif action == cls.SET:
            cnf.set[key] = value
