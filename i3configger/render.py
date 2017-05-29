import logging
from collections import defaultdict

log = logging.getLogger(__name__)


class Renderer:
    @staticmethod
    def resolve():
        resolvedVars = vars_.copy()
        """resolve values that are vars_ (e.g. set $var $ otherVar)"""
        for key, value in resolvedVars.items():
            if value.startswith('$'):
                try:
                    resolvedVars[key] = resolvedVars[value]
                except KeyError:
                    log.exception("[IGNORED] %s, %s", key, value)
        return resolvedVars
