import logging
import time
import typing as t
from pathlib import Path
from string import Template

from i3configger import context, partials, base

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, sourcePath: Path, targetPath: Path, suffix: str,
                 selectorMap: t.Union[None, dict]=None, dryRun: bool=False):
        self.sourcePath = sourcePath
        self.mainTargetPath = targetPath
        self.suffix = suffix
        self.selectorMap = selectorMap or {}
        self.dryRun = dryRun
        log.info("initialized %s", self)

    def build_all(self):
        prts, ctx, settings = self.prepare()
        self.build_main(prts, ctx)
        if any(prt.i3status for prt in prts):
            self.build_i3status(prts, ctx, settings)

    def prepare(self):
        prts = partials.create(self.sourcePath, self.suffix)
        ctx, settings = context.create(prts)
        return prts, ctx, settings

    def build_main(self, prts, ctx):
        content = partials.get_content(
            prts, self.selectorMap, excludes=base.BAR_EXCLUDES)
        substituted = self.substitute(content, ctx)
        complete = "%s\n\n%s" % (self.get_header(), substituted)
        if self.dryRun:
            print(complete)
        else:
            self.mainTargetPath.write_text(complete)

    def build_i3status(self, prts, ctx, settings):
        prts = [prt for prt in prts if prt.i3status]
        if not prts:
            log.info("no configuration for status found")
            return
        barTpl = partials.find(prts, 'tpl', 'bar')
        if not barTpl:
            log.warning("can't build: no template found")
        barConfigs = [prt for prt in prts if prt.key == 'bar']
        if not barConfigs:
            log.warning("can't build: no bar configs found")
        elif not settings:
            log.warning("can't build: no settings for status found")
        else:
            marker = base.VAR_MARK + base.I3STATUS_BAR_MARKER + '_'
            defaultKey = marker + 'default'
            defaults = settings.get(defaultKey, {})
            del settings[defaultKey]
            root = Path(defaults['bar_target_root']).expanduser()
            for prt in [prt for prt in prts if prt.key == 'bar']:
                substituted = self.substitute(prt.payload, ctx)
                (root / prt.name).write_text(substituted)
            for barId, map_ in settings.items():
                barId = barId[len(marker):]
                map_[base.BAR_VAR_MARKER + 'id'] = barId
                subs = defaults.copy()
                subs.update(ctx)
                subs.update(map_)
                targetPath = root / ("%s.conf" % barId)
                subs['bar_target_path'] = targetPath
                cnt = self.substitute(barTpl.payload, subs)
                complete = "%s\n\n%s" % (self.get_header(), cnt)
                if self.dryRun:
                    print(complete)
                else:
                    targetPath.write_text(complete)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        template = Template(content)
        cleaned = {}
        for key, value in ctx.items():
            key = key[1:] if key.startswith(base.VAR_MARK) else key
            cleaned[key] = value
        renderedContent = template.safe_substitute(cleaned)
        return renderedContent

    def get_header(self):
        msg = (f'# Generated from {self.sourcePath} by i3configger '
               f'({time.asctime()}) #')
        sep = "#" * len(msg)
        return "%s\n%s\n%s" % (sep, msg, sep)
