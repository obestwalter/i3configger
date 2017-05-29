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

    def build_all(self):
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
        allUsedSources = set([s["source"] for s in i3s.bars.values()])
        for source in allUsedSources:
            prt = partials.find(prts, i3s.marker, source)
            assert isinstance(prt, partials.Partial), prt
            localCtx = dict(ctx)
            cnt = self.substitute(prt.payload, localCtx)
            targetRoot = Path(i3s.target).expanduser()
            targetPath = targetRoot / ("%s.%s.conf" % (i3s.marker, source))
            targetPath.write_text(cnt)

        with self.mainTargetPath.open('a') as f:
            for barName, barCtx in i3s.bars.items():
                barCtx["id"] = barName
                prt = partials.find(prts, i3s.marker, barCtx[i3s.TEMPLATE])
                localCtx = dict(ctx)
                localCtx.update(barCtx)
                cnt = "### %s ###\n" % barName
                cnt += self.substitute(prt.payload, localCtx)
                f.write(cnt + '\n')

        # barTpl = partials.find(prts, 'tpl', 'bar')
        # if not barTpl:
        #     log.warning("can't build: no template found")
        # barConfigs = [prt for prt in prts if prt.key == 'bar']
        # if not barConfigs:
        #     log.warning("can't build: no bar configs found")
        # elif not settings:
        #     log.warning("can't build: no settings for status found")
        # else:
        #     marker = base.VAR_MARK + base.I3STATUS_BAR_MARKER + '_'
        #     defaultKey = marker + 'default'
        #     defaults = settings.get(defaultKey, {})
        #     del settings[defaultKey]
        #     root = Path(defaults['bar_target_root']).expanduser()
        #     for prt in [prt for prt in prts if prt.key == 'bar']:
        #         substituted = self.substitute(prt.payload, ctx)
        #         (root / prt.name).write_text(substituted)
        #     for barId, map_ in settings.items():
        #         barId = barId[len(marker):]
        #         map_[base.BAR_VAR_MARKER + 'id'] = barId
        #         subs = defaults.copy()
        #         subs.update(ctx)
        #         subs.update(map_)
        #         targetPath = root / ("%s.conf" % barId)
        #         subs['bar_target_path'] = targetPath
        #         cnt = self.substitute(barTpl.payload, subs)
        #         complete = "%s\n\n%s" % (self.get_header(), cnt)

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
