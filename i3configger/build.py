import logging
import os
import tempfile
import time
from pathlib import Path

from i3configger import (
    __version__, base, config, context, exc, ipc, partials, state)

log = logging.getLogger(__name__)


def build_all(configPath):
    cnf = config.I3configgerConfig(configPath)
    pathContentsMap = generate_contents(cnf)
    check_config(pathContentsMap[cnf.mainTargetPath])
    persist_results(pathContentsMap)


def generate_contents(cnf):
    prts = partials.create(cnf.partialsPath)
    st = state.process(cnf.statePath, prts, cnf.message)
    pathContentsMap = {}
    excludes = {b["key"] for b in cnf.barTargets.values()}
    selectorMap = st["select"]
    selected = partials.select(prts, selectorMap, excludes)
    ctx = context.merge(selected)
    mainContent = generate_main_content(cnf.partialsPath, selected, ctx)
    for barName, barCnf in cnf.barTargets.items():
        barCnf["id"] = barName
        eCtx = context.merge([ctx, barCnf, st["set"]])
        mainContent += "\n%s" % generate_bar_setting(barCnf, prts, eCtx)
        statusFileContent = generate_status_file_content(
            prts, barCnf["key"], barCnf["value"], eCtx)
        if statusFileContent:
            filename = f"{barCnf['key']}.{barCnf['value']}{base.SUFFIX}"
            dst = Path(barCnf["target"]) / filename
            pathContentsMap[dst] = statusFileContent
    pathContentsMap[cnf.mainTargetPath] = mainContent.rstrip('\n') + '\n'
    return pathContentsMap


def make_header(partialsPath):
    strPath = str(partialsPath)
    parts = strPath.split(os.getenv('HOME'))
    if len(parts) > 1:
        strPath = "~" + parts[-1]
    msg = (f'# Built from {strPath} by i3configger {__version__} '
           f'({time.asctime()}) #')
    sep = "#" * len(msg)
    return "%s\n%s\n%s\n" % (sep, msg, sep)


def generate_main_content(partialsPath, selected, ctx):
    content = make_header(partialsPath)
    content += '\n'.join(prt.display for prt in selected if prt.display)
    return context.substitute(content, ctx).rstrip('\n') + '\n\n'


def generate_bar_setting(barCnf, prts, ctx):
    tpl = partials.find(prts, barCnf["key"], barCnf["template"])
    assert isinstance(tpl, partials.Partial), tpl
    return context.substitute(tpl.display, ctx).rstrip('\n')


def generate_status_file_content(prts, selectKey, selectValue, ctx):
    prt = partials.find(prts, selectKey, selectValue)
    if not prt:
        log.warning("[IGNORE] no status config named %s.%s%s",
                    selectKey, selectKey, base.SUFFIX)
        return
    assert isinstance(prt, partials.Partial), prt
    return context.substitute(prt.display, ctx).rstrip('\n') + '\n'


def check_config(content):
    tmpPath = Path(tempfile.gettempdir()) / 'i3config_check'
    tmpPath.write_text(content)
    errorReport = ipc.I3.get_config_errors(tmpPath)
    if errorReport:
        raise exc.ConfigError(
            f"config:\n{content}\n\nerrors:\n{errorReport.decode()}"
            f"FATAL: config not changed due to errors.")


def persist_results(pathContentsMap):
    for path, content in pathContentsMap.items():
        path.write_text(content)
