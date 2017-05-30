import sys
from pathlib import Path

from i3configger import base, build, config, context, partials


def test_build():
    base.DEBUG = 0
    d = config.DEFAULT
    builder = build.Builder(
        d.SOURCES_PATH, d.TARGET_PATH, d.SOURCE_SUFFIX)
    builder.build()
