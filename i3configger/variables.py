import re

import logging

log = logging.getLogger(__name__)

ASSIGNMENT_RE = re.compile(r'(\$\S+)\s+(.*)')
VARIABLES = {}


def render_vars(content):
    """grab, resolve and remove $prefix for string substitution"""
    grab_variables(content)
    resolve_variables()
    return {key[1:]: value for key, value in VARIABLES.items()}


def grab_variables(content):
    for line in [l.strip() for l in content.splitlines()]:
        if looks_like_assignment(line):
            key, value = get_assignment(line)
            VARIABLES[key] = value


def resolve_variables():
    """resolve values that are vars_ (e.g. set $var $ otherVar)"""
    for key, value in VARIABLES.items():
        if value.startswith('$'):
            try:
                VARIABLES[key] = VARIABLES[value]
            except KeyError:
                log.exception("[IGNORED] %s, %s", key, value)


def looks_like_assignment(line):
    return line.strip().startswith('set ')


def get_assignment(line):
    sanitizedLine = (line.split('set')[1].split(' # ')[0]).strip()
    if len([c for c in sanitizedLine if c == '#']) > 1:
        raise MalformedAssignment("comments need space: '%s'", line)
    match = re.match(ASSIGNMENT_RE, sanitizedLine)
    if not match or len(match.groups()) != 2:
        raise MalformedAssignment("can't match properly: '%s'", line)
    return match.group(1), match.group(2)


class MalformedAssignment(Exception):
    pass
