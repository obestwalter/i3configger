import json
import logging
import pprint
import time
import typing as t
from pathlib import Path
from string import Template

from i3configger import base, config, context, partials, exc

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, sourcePath: Path, targetPath: Path, suffix: str,
                 selectors: t.Union[None, dict]=None, command=None):
        self.sourcePath = sourcePath
        self.mainTargetPath = targetPath
        self.suffix = suffix
        self.selectors = selectors or {}
        self.command = command   # TODO do something with this (but only once)
        self.cnf = config.I3configgerConfig(self.sourcePath)
        log.info("initialized %s", self)

    def __str__(self):
        return "%s\n%s" % (self.__class__.__name__, pprint.pformat(vars(self)))

    def build(self):
        allPrts = partials.create(self.sourcePath, self.suffix)
        excludes = [self.cnf.marker] if self.cnf.hasStatusConfig else None
        with open(self.sourcePath / 'saved-selector.json') as f:
            savedSelector = json.load(f)
        selected = partials.select(
            allPrts, self.selectors, excludes, savedSelector=savedSelector)
        if not selected:
            raise exc.I3configgerException(
                "No content for %s, %s, %s", allPrts, self.selectors, excludes)
        ctx = context.create(selected)
        self.build_main(selected, ctx)
        if self.cnf.hasStatusConfig:
            self.build_i3status(allPrts, ctx)

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
