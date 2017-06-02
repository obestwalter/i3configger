import logging
import os
import pprint
import time
from pathlib import Path
from string import Template

from i3configger import base, config, context, exc, ipc, partials

log = logging.getLogger(__name__)


class Builder:
    STAGING_SUFFIX = '.staged'

    def __init__(self, cnf: config.I3configgerConfig):
        self.cnf = cnf
        self.results = {}
        """name -> (tmp path, target path)"""
        log.info("initialized %s", self)

    def __str__(self):
        return "%s\n%s" % (self.__class__.__name__, pprint.pformat(vars(self)))

    def build(self):
        prts = partials.create(self.cnf.partialsPath)
        excludes = {b["select-key"] for b in self.cnf.bars.values()}
        selected = partials.select(prts, self.cnf.select, excludes=excludes)
        if not selected:
            raise exc.I3configgerException(
                "no content for %s, %s, %s", prts, self.cnf)
        ctx = context.create(selected)
        rawContent = self.make_header()
        rawContent += '\n'.join(prt.display for prt in selected)
        if self.cnf.bars:
            rawContent += self.make_bars(prts, ctx)
        resolvedContent = self.substitute(rawContent, ctx)
        container = self.cnf.mainTargetPath.parent
        targetName = self.cnf.mainTargetPath.name
        tmpPath = container / (targetName + self.STAGING_SUFFIX)
        tmpPath.write_text(resolvedContent)
        self.results[tmpPath] = self.cnf.mainTargetPath
        self.freeze_if_ok(self.results)

    @staticmethod
    def freeze_if_ok(results):
        for tmpPath in results.values():
            # TODO generated status configs seem always ok?
            if not ipc.I3.config_is_ok(tmpPath):
                raise exc.BuildError(f"{tmpPath} is broken")
            for line in tmpPath.read_text().splitlines():
                if base.VAR_MARK in line:
                    raise exc.BuildError(f"not all vars resolved in {tmpPath}")
        # all or nothing
        for src, dst in results.items():
            log.info(f"{src} -> {dst}")
            os.rename(src, dst)

    def make_bars(self, prts, ctx):
        bars = []
        for barName, barCnf in self.cnf.bars.items():
            barCnf["id"] = barName
            selectKey = barCnf["select-key"]
            selectValue = barCnf["select-value"]
            prt = partials.find(prts, selectKey, selectValue)
            assert isinstance(prt, partials.Partial), prt
            tpl = partials.find(prts, selectKey, barCnf["template"])
            assert isinstance(tpl, partials.Partial), tpl
            eCtx = context.enhance(ctx, [barCnf, prt, self.cnf.set])
            bars.append(self.substitute(tpl.display, eCtx))
            if prt.name not in self.results:
                content = self.substitute(prt.payload, eCtx)
                container = Path(barCnf["target"])
                if not container.is_absolute():
                    container = (self.cnf.partialsPath / container).resolve()
                tmpPath = container / f"{prt.name}{self.STAGING_SUFFIX}"
                self.results[tmpPath] = container / f"{prt.name}{base.SUFFIX}"
                tmpPath.write_text(content)
        return '\n'.join(bars)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        return Template(content).safe_substitute(ctx)

    def make_header(self):
        msg = f'# Generated from {self.cnf.configPath} ({time.asctime()}) #'
        sep = "#" * len(msg)
        return "%s\n%s\n%s" % (sep, msg, sep)
