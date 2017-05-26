import pprint
import tempfile
from pathlib import Path

PROJECT_PATH = Path(__file__).parents[1]
LOG_PATH = Path(tempfile.gettempdir()) / 'i3configger.log'
SOURCES_PATH = Path('~/.i3/config.d').expanduser()
TARGET_PATH = Path('~/.i3/config').expanduser()
SOURCE_SUFFIX = '.conf'
STATUS_MARKER = 'i3status'


if __name__ == '__main__':
    pprint.pprint(locals())
