import logging
import pprint
import time
from string import Template

from i3configger import base, context, partials

log = logging.getLogger(__name__)


class I3Configger:
    def __init__(self, sourcePath, targetPath, suffix, selectorMap=None):
        self.sourcePath = sourcePath
        self.mainTargetPath = targetPath
        self.suffix = suffix
        self.selectorMap = selectorMap or {}
        log.info("initialized %s", self)

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__, pprint.pformat(self.__dict__))

    def build_all(self):
        prts = partials.create(self.sourcePath, self.suffix)
        ctx = context.create(prts)
        self.build_main()
        self.build_i3status()

    def build_main(self):
        pass

    def build_i3status(self):
        pass

    def get_content(self, prts, selectorMap):
        selected = partials.select(prts, selectorMap)
        return ''.join(p.prepared for p in selected)

    def render(self):
        substituted = self.substitute(joined)
        self.mainTargetPath.write_text(substituted)

    @classmethod
    def substitute(cls, content, ctx):
        """Substitute all variables with their values.

        Works almost out of the box, because '$' is the standard substitution
        marker for string.Template
        """
        template = Template(content)
        cleanCtx = context.cleaned_for_substitution(ctx)
        renderedContent = template.safe_substitute(cleanCtx)
        return renderedContent

    def get_header(self):
        msg = (f'# Generated from {self.sourcePath} by i3configger '
               f'({time.asctime()}) #')
        sep = "#" * len(msg)
        return '\n'.join("%s\n%s\n%s\n" % (sep, msg, sep)) + '\n'
