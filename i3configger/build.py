"""High level build functionality bringing it all together."""
import logging
import os
import tempfile
import time
from pathlib import Path
from pprint import pformat

from i3configger import config, context, exc, ipc, message, partials

log = logging.getLogger(__name__)


def build_all():
    cnf = config.I3configgerConfig()
    log.info(f"start building from {cnf.partialsPath}")
    prts = partials.create(cnf.partialsPath)
    msg = message.Messenger(cnf.messagesPath, prts).fetch_messages(
        exludes=[config.I3BAR]
    )
    cnf.payload = context.merge(cnf.payload, msg[message.CMD.SHADOW])
    pathContentsMap = generate_contents(cnf, prts, msg)
    check_config(pathContentsMap[cnf.targetPath])
    persist_results(pathContentsMap)
    ipc.communicate(refresh=True)
    log.info("build done")


def generate_contents(cnf: config.I3configgerConfig, prts, msg):
    selectorMap = msg[message.CMD.SELECT]
    setMap = msg[message.CMD.SET]
    pathContentsMap = {}
    barTargets = cnf.get_bar_targets()
    selected = partials.select(prts, selectorMap, excludes=[config.I3BAR])
    ctx = context.process(selected + [setMap])
    log.debug(f"main context:\n{pformat(ctx)}")
    mainContent = generate_main_content(cnf.partialsPath, selected, ctx)
    for barName, barCnf in barTargets.items():
        barCnf["id"] = barName
        log.debug(f"bar {barName} config:\n{pformat(barCnf)}")
        extendedContext = context.process([ctx, barCnf])
        mainContent += f"\n{get_bar_setting(barCnf, prts, extendedContext)}"
        i3barFileContent = generate_i3bar_content(
            prts, barCnf["select"], extendedContext
        )
        if i3barFileContent:
            filename = f"{config.I3BAR}.{barCnf['select']}{config.SUFFIX}"
            dst = Path(barCnf["target"]) / filename
            pathContentsMap[dst] = i3barFileContent
    pathContentsMap[cnf.targetPath] = mainContent.rstrip("\n") + "\n"
    return pathContentsMap


def make_header(partialsPath):
    strPath = str(partialsPath)
    parts = strPath.split(os.getenv("HOME"))
    if len(parts) > 1:
        strPath = "~" + parts[-1]
    msg = f"# Built from {strPath} by i3configger ({time.asctime()}) #"
    sep = "#" * len(msg)
    return f"{sep}\n{msg}\n{sep}\n"


def generate_main_content(partialsPath, selected, ctx):
    out = [make_header(partialsPath)]
    for prt in selected:
        content = prt.get_pruned_content()
        if content:
            out.append(content)
    return context.substitute("\n".join(out), ctx).rstrip("\n") + "\n\n"


def get_bar_setting(barCnf, prts, ctx):
    tpl = partials.find(prts, config.I3BAR, barCnf["template"])
    assert isinstance(tpl, partials.Partial), tpl
    tpl.name = f"{tpl.name} [id: {barCnf['id']}]"
    return context.substitute(tpl.get_pruned_content(), ctx).rstrip("\n")


def generate_i3bar_content(prts, selectValue, ctx):
    prt = partials.find(prts, config.I3BAR, selectValue)
    if not prt:
        raise exc.ConfigError(
            f"[IGNORE] no status config named "
            f"{config.I3BAR}.{selectValue}{config.SUFFIX}"
        )
    assert isinstance(prt, partials.Partial), prt
    content = context.substitute(prt.get_pruned_content(), ctx)
    return content.rstrip("\n") + "\n"


def check_config(content):
    tmpPath = Path(tempfile.gettempdir()) / "i3config_check"
    tmpPath.write_text(content)
    errorReport = ipc.I3.get_config_error_report(tmpPath)
    if errorReport:
        msg = (
            f"FATAL: config not changed due to errors. "
            f"Broken config is at {tmpPath}"
        )
        report = f"config:\n{content}\n\nerrors:\n{errorReport}"
        ipc.communicate(msg, urgency="normal")
        raise exc.ConfigError(f"{msg}\n{report}")


def persist_results(pathContentsMap):
    for path, content in pathContentsMap.items():
        backupPath = Path(str(path) + ".bak")
        if path.exists() and not backupPath.exists():
            path.rename(backupPath)
        path.write_text(content)
