import logging
import time
import typing as t
from pathlib import Path
from string import Template

from i3configger import base, context, partials
from i3configger.base import I3Status

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, sourcePath: Path, targetPath: Path, suffix: str,
                 selectorMap: t.Union[None, dict]=None):
        self.sourcePath = sourcePath
        self.mainTargetPath = targetPath
        self.suffix = suffix
        self.selectorMap = selectorMap or {}
        self.i3s = base.I3Status(self.sourcePath)
        log.info("initialized %s", self)

    def build(self):
        prts = partials.create(self.sourcePath, self.suffix)
        ctx = context.create(prts)
        i3s = I3Status(self.sourcePath)
        self.build_main(prts, ctx, [i3s.marker] if i3s else None)
        if i3s:
            self.build_i3status(prts, ctx, i3s)

    def build_main(self, prts, ctx, excludes):
        content = partials.get_content(prts, self.selectorMap, excludes)
        substituted = self.substitute(content, ctx)
        complete = "%s\n\n%s" % (self.get_header(), substituted)
        self.mainTargetPath.write_text(complete)

    def build_i3status(self, prts: t.List[partials.Partial],
                       ctx: dict, i3s: I3Status):
        self._build_bar_configs(prts, ctx, i3s)
        self._add_bar_settings(prts, ctx, i3s)

    def _add_bar_settings(self, prts, ctx, i3s):
        with self.mainTargetPath.open('a') as f:
            for barName, barCtx in i3s.bars.items():
                barCtx["id"] = barName
                prt = partials.find(prts, i3s.marker, barCtx[i3s.TEMPLATE])
                localCtx = dict(ctx)
                localCtx.update(barCtx)
                cnt = self.substitute(prt.payload, localCtx)
                f.write(cnt + '\n')

    @classmethod
    def _build_bar_configs(cls, prts, ctx, i3s):
        allUsedSources = set([s[i3s.SOURCE] for s in i3s.bars.values()])
        for source in allUsedSources:
            prt = partials.find(prts, i3s.marker, source)
            assert isinstance(prt, partials.Partial), prt
            localCtx = dict(ctx)
            sourceCnt = cls.substitute(prt.payload, localCtx)
            targetRoot = Path(i3s.target).expanduser()
            targetPath = targetRoot / ("%s.%s.conf" % (i3s.marker, source))
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
