import sys
from pathlib import Path

from i3configger import base, build, config, context, partials

HERE = Path(__file__).parent
EXAMPLES = HERE.parent / 'examples'
TARGET = HERE / 'target'


def test_build():
    base.DEBUG = 0
    d = config.DEFAULT
    builder = build.Builder(EXAMPLES / 'default', TARGET, d.suffix)
    builder.build()
