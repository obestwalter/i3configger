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
        content = self.render()
        self.persist(content, self.cnf.mainTargetPath)

    def render(self):
        prts = partials.create(self.cnf.partialsPath)
        excludes = {b["key"] for b in self.cnf.bars.values()}
        selected = partials.select(
            prts, self.cnf.state["select"], excludes=excludes)
        if not selected:
            raise exc.I3configgerException(
                "no content for %s, %s, %s", prts, self.cnf)
        ctx = context.create(selected)
        rawContent = self.make_header()
        rawContent += '\n'.join(prt.display for prt in selected)
        resolvedContent = self.substitute(rawContent, ctx)
        if not self.cnf.bars:
            return resolvedContent
        barContent = self.get_bar_content(prts, ctx, self.cnf.state)
        return "%s\n%s" % (resolvedContent, barContent)

    def persist(self, content, path):
        container = path.parent
        targetName = path.name
        tmpPath = container / (targetName + self.STAGING_SUFFIX)
        tmpPath.write_text(content)
        self.results[tmpPath] = self.cnf.mainTargetPath
        self.freeze_if_ok(self.results)

    @classmethod
    def freeze_if_ok(cls, results):
        for tmpPath in results.values():
            # TODO generated status configs seem always ok?
            if not ipc.I3.config_is_ok(tmpPath):
                raise exc.BuildError(f"{tmpPath} is broken")
        # cls.ensure_all_vars_are_resolved(results)
        for src, dst in results.items():  # all or nothing
            log.info(f"{src} -> {dst}")
            os.rename(src, dst)

    def ensure_all_vars_are_resolved(self, results):
        # FIXME would only work, if marker was unique-ish (not just $)
        # TODO mask all $ **not** in set statements with a tmp marker
        # not found anywhere in the content
        # check all vars are resolved and then put the masked $ back in
        for tmpPath in results.values():
            for line in tmpPath.read_text().splitlines():
                if base.VAR_MARK in line:
                    raise exc.BuildError(f"not all vars resolved in {tmpPath}")

    def get_bar_content(self, prts, ctx, state):
        bars = []
        for barName, barCnf in self.cnf.bars.items():
            barCnf["id"] = barName
            selectKey = barCnf["key"]
            selectValue = barCnf["value"]
            prt = partials.find(prts, selectKey, selectValue)
            assert isinstance(prt, partials.Partial), prt
            tpl = partials.find(prts, selectKey, barCnf["template"])
            assert isinstance(tpl, partials.Partial), tpl
            container = Path(barCnf["target"])
            if not container.is_absolute():
                container = (self.cnf.partialsPath / container).resolve()
                barCnf["target"] = str(container)
            eCtx = context.enhance(ctx, [barCnf, prt, state["set"]])
            bars.append(self.substitute(tpl.display, eCtx))
            if prt.name not in self.results:
                content = self.substitute(prt.payload, eCtx)
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
