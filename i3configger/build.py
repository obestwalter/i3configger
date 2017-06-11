import logging
import os
import tempfile
import time
from pathlib import Path
from pprint import pformat

from i3configger import base, config, context, exc, ipc, message, partials, \
    paths

log = logging.getLogger(__name__)


def build_all(configPath):
    log.info(f"start building from {configPath}")
    p = paths.Paths(configPath)
    prts = partials.create(p.root)
    cnf = config.I3configgerConfig(configPath)
    msg = message.Messenger(p.messages, prts).fetch_messages()
    cnf.payload = context.merge(cnf.payload, msg[message.CMD.SHADOW])
    pathContentsMap = generate_contents(
        cnf, prts, msg[message.CMD.SELECT], msg[message.CMD.SET])
    check_config(pathContentsMap[cnf.mainTargetPath])
    persist_results(pathContentsMap)
    log.info(f"build from {configPath} done")


def generate_contents(cnf, prts, selectorMap, setMap):
    pathContentsMap = {}
    barTargets = cnf.get_bar_targets()
    excludes = {b["key"] for b in barTargets.values()}
    selected = partials.select(prts, selectorMap, excludes)
    ctx = context.process(selected + [setMap])
    ctx = context.resolve_variables(ctx)
    ctx = context.remove_variable_markers(ctx)
    log.info(f"main context:\n{pformat(ctx)}")
    mainContent = generate_main_content(cnf.partialsPath, selected, ctx)
    for barName, barCnf in barTargets.items():
        barCnf["id"] = barName
        eCtx = context.process([ctx, barCnf])
        log.info(f"bar {barName} context:\n{pformat(eCtx)}")
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
    msg = f'# Built from {strPath} by i3configger ({time.asctime()}) #'
    sep = "#" * len(msg)
    return "%s\n%s\n%s\n" % (sep, msg, sep)


def generate_main_content(partialsPath, selected, ctx):
    out = [make_header(partialsPath)]
    for prt in selected:
        content = prt.get_pruned_content()
        if content:
            out.append(content)
    return context.substitute('\n'.join(out), ctx).rstrip('\n') + '\n\n'


def generate_bar_setting(barCnf, prts, ctx):
    tpl = partials.find(prts, barCnf["key"], barCnf["template"])
    assert isinstance(tpl, partials.Partial), tpl
    return context.substitute(tpl.get_pruned_content(), ctx).rstrip('\n')


def generate_status_file_content(prts, selectKey, selectValue, ctx):
    prt = partials.find(prts, selectKey, selectValue)
    if not prt:
        log.warning("[IGNORE] no status config named %s.%s%s",
                    selectKey, selectKey, base.SUFFIX)
        return
    assert isinstance(prt, partials.Partial), prt
    content = context.substitute(prt.get_pruned_content(), ctx)
    return content.rstrip('\n') + '\n'


def check_config(content):
    tmpPath = Path(tempfile.gettempdir()) / 'i3config_check'
    tmpPath.write_text(content)
    errorReport = ipc.I3.get_config_error_report(tmpPath)
    if errorReport:
        raise exc.ConfigError(
            f"config:\n{content}\n\nerrors:\n{errorReport}"
            f"FATAL: config not changed due to errors. "
            f"Broken config is at {tmpPath}")


def persist_results(pathContentsMap):
    for path, content in pathContentsMap.items():
        backupPath = Path(str(path) + '.bak')
        if not backupPath.exists():
            path.rename(backupPath)
        path.write_text(content)
