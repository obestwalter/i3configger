import logging
import os
import pprint
import time
from pathlib import Path
from string import Template

from i3configger import config, context, exc, partials, ipc
from i3configger.config import KEY

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, cnf: config.I3configgerConfig):
        self.cnf = cnf
        self.results = {}
        """name -> (tmp path, target path)"""
        log.info("initialized %s", self)

    def __str__(self):
        return "%s\n%s" % (self.__class__.__name__, pprint.pformat(vars(self)))

    def build(self):
        prts = partials.create(self.cnf.partialsPath, self.cnf.suffix)
        selected = partials.select(
            prts, self.cnf.select, excludes={b.marker for b in self.cnf.bars})
        if not selected:
            raise exc.I3configgerException(
                "no content for %s, %s, %s", prts, self.cnf)
        ctx = context.create(selected)
        rawContent = self.make_header()
        rawContent += '\n'.join(prt.display for prt in prts)
        if self.cnf.bars:
            rawContent += self.make_bars(prts, ctx)
        resolvedContent = self.substitute(rawContent, ctx)
        tmpPath = self.cnf.targetPath / (self.cnf.name + '.tmp')
        tmpPath.write_text(resolvedContent)
        self.results["main"] = (tmpPath, self.cnf.targetPath / self.cnf.name)
        if ipc.I3.config_is_ok(tmpPath):
            # TODO can I check generated status configs also?
            for srcPath, dstPath in self.results.items():
                os.rename(srcPath, dstPath)

    def make_bars(self, prts, ctx):
        bars = []
        for barName, barCnf in self.cnf.bars.items():
            barCnf["id"] = barName
            marker = barCnf[KEY.MARKER]
            selector = barCnf[KEY.SELECTOR]
            prt = partials.find(prts, marker, selector)
            assert isinstance(prt, partials.Partial), prt
            tpl = partials.find(prts, barCnf[KEY.MARKER], barCnf[KEY.TEMPLATE])
            assert isinstance(tpl, partials.Partial), tpl
            localCtx = dict(ctx)
            localCtx.update(barCnf)
            localCtx.update(context.create([prt]))
            bars.append(self.substitute(tpl, localCtx))
            if prt.name not in self.results:
                marker = barCnf[KEY.TARGET]
                root = Path(marker).expanduser()
                path = root / ("%s.%s.conf" % (marker, selector))
                content = self.substitute(prt.payload, localCtx)
                path.write_text(content)
                self.results[prt.name] = ()
        return '\n'.join(bars)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        return Template(content).safe_substitute(ctx)

    def make_header(self):
        msg = (f'# Generated from {self.cnf.partialsPath} by i3configger '
               f'({time.asctime()}) #')
        sep = "#" * len(msg)
        return "%s\n%s\n%s" % (sep, msg, sep)
