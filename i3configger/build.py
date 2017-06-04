import logging
import os
import pprint
import time
from pathlib import Path
from string import Template

from i3configger import __version__, base, config, context, exc, ipc, partials

log = logging.getLogger(__name__)


class Builder:
    def __init__(self, configPath):
        self.cnf = config.I3configgerConfig(configPath)
        log.info("initialized %s", self)

    def __str__(self):
        return "%s\n%s" % (self.__class__.__name__, pprint.pformat(vars(self)))

    def build(self):
        content = self._build()
        self.persist_main(content, self.cnf.mainTargetPath)

    def _build(self):
        prts = partials.create(self.cnf.partialsPath)
        excludes = {b["key"] for b in self.cnf.barTargets.values()}
        selected = partials.select(prts, self.cnf.state["select"], excludes)
        content = self.make_header()
        ctx = context.create(selected)
        if selected:
            content += '\n'.join(prt.display for prt in selected)
            content = self.substitute(content, ctx)
        barContent = self.get_bar_content(prts, ctx, self.cnf.state)
        if barContent:
            content = "%s\n%s" % (content, barContent)
        return content.rstrip('\n') + '\n'

    def persist_main(self, content, path):
        container = path.parent
        targetName = path.name
        backupPath = container / (targetName + '.bak')
        if self.cnf.mainTargetPath.exists():
            os.rename(self.cnf.mainTargetPath, backupPath)
        try:
            self.cnf.mainTargetPath.write_text(content)
            if not ipc.I3.config_is_ok(self.cnf.mainTargetPath):
                brokenPath = container / (targetName + '.broken')
                os.rename(self.cnf.mainTargetPath, brokenPath)
                raise exc.BuildError(f"{brokenPath} is broken")
        except:
            os.rename(backupPath, self.cnf.mainTargetPath)
            raise

    def get_bar_content(self, prts, ctx, state):
        bars = []
        alreadyWritten = []
        for barName, barCnf in self.cnf.barTargets.items():
            barCnf["id"] = barName
            selectKey = barCnf["key"]
            selectValue = barCnf["value"]
            prt = partials.find(prts, selectKey, selectValue)
            if not prt:
                log.warning(
                    "[IGNORE ]no bar %s.%s%s found",
                    selectKey, selectKey, base.SUFFIX)
                continue
            assert isinstance(prt, partials.Partial), prt
            tpl = partials.find(prts, selectKey, barCnf["template"])
            assert isinstance(tpl, partials.Partial), tpl
            container = Path(barCnf["target"])
            if not container.is_absolute():
                container = (self.cnf.partialsPath / container).resolve()
                barCnf["target"] = str(container)
            eCtx = context.enhance(ctx, [barCnf, prt, state["set"]])
            bars.append(self.substitute(tpl.display, eCtx))
            if prt.name not in alreadyWritten:
                content = self.substitute(prt.payload, eCtx)
                path = container / f"{prt.name}{base.SUFFIX}"
                path.write_text(content + '\n')
                alreadyWritten.append(path)
        return '\n'.join(bars)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        return Template(content).safe_substitute(ctx)

    def make_header(self):
        strPath = str(self.cnf.partialsPath)
        parts = strPath.split(os.getenv('HOME'))
        if len(parts) > 1:
            strPath = "~" + parts[-1]
        msg = (f'# Built from {strPath} by i3configger {__version__} '
               f'({time.asctime()}) #')
        sep = "#" * len(msg)
        return "%s\n%s\n%s\n" % (sep, msg, sep)
